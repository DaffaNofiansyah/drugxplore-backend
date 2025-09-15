from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.views import APIView
import csv
import io
from django.shortcuts import get_object_or_404
from django.utils import timezone
import pubchempy as pcp
import requests
from rdkit import Chem
from rdkit.Chem import Crippen
from rest_framework.response import Response
from concurrent.futures import ThreadPoolExecutor, as_completed
from .serializers import PredictionSerializer
from rest_framework.permissions import IsAuthenticated
from api.models import Prediction, Compound, PredictionCompound, MLModel
from drf_spectacular.utils import extend_schema_view, extend_schema
from .schemas import (
    prediction_list_schema,
    prediction_retrieve_schema,
    prediction_destroy_schema,
    predict_ic50_schema,
    prediction_download_schema
)
import environ
env = environ.Env()
environ.Env.read_env()

@extend_schema_view(
    list=extend_schema(**prediction_list_schema),
    retrieve=extend_schema(**prediction_retrieve_schema),
    destroy=extend_schema(**prediction_destroy_schema)
)
class PredictionViewSet(viewsets.ModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = Prediction.objects.all() if self.request.user.role == 'admin' else Prediction.objects.filter(user=self.request.user)
        return qs.select_related('ml_model', 'user').prefetch_related('prediction_compounds__compound').order_by('-created_at') 

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Predictions retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "message": "Prediction retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "status": "success",
            "message": "Prediction deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

class PredictIC50View(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**predict_ic50_schema)
    def post(self, request, *args, **kwargs):
        user = request.user
        csv_file = request.FILES.get("file", None)
        smiles_input = request.data.get("smiles", None)
        model_descriptor = request.data.get("model_descriptor", None)
        model_method = request.data.get("model_method", None)

        if not all([model_descriptor, model_method]):
            return Response(
                {"error": "model_descriptor and model_method are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if csv_file:
            if not csv_file.name.endswith(".csv"):
                return Response({"error": "Only CSV files are supported."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                decoded_file = csv_file.read().decode("utf-8-sig")
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                smiles_list = [row[0].strip() for row in reader if row and row[0].strip()]
            except Exception as e:
                return Response({"error": f"Failed to parse CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elif smiles_input:
            if isinstance(smiles_input, str):
                smiles_list = [s.strip() for s in smiles_input.split(",") if s.strip()]
            elif isinstance(smiles_input, list):
                smiles_list = [s.strip() for s in smiles_input if isinstance(s, str) and s.strip()]
            else:
                return Response({"error": "SMILES input must be a comma-separated string or a list of strings."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Provide either a 'smiles' field or a 'file' (CSV)."}, status=status.HTTP_400_BAD_REQUEST)

        seen = set()
        smiles_list = [s for s in smiles_list if not (s in seen or seen.add(s))]

        if not smiles_list:
            return Response({"error": "No valid SMILES strings provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ml_predict_url = "http://localhost:8080/api/v1/predict/"
            response = requests.post(ml_predict_url, json={
                "smiles": smiles_list,
                "model_method": model_method,
                "model_descriptor": model_descriptor,
                "input_source_type": "csv" if csv_file else "text",
            })

            if response.status_code != 200:
                return Response({"error": "ML prediction API error.", "details": response.json().get("detail")}, status=status.HTTP_400_BAD_REQUEST)

            predictions = response.json()
            if "error" in predictions:
                return Response(predictions, status=status.HTTP_400_BAD_REQUEST)

            if not predictions:
                return Response({"error": "No predictions returned from ML API."}, status=status.HTTP_400_BAD_REQUEST)

            ml_model = get_object_or_404(MLModel, descriptor=model_descriptor, method=model_method, is_active=True)
            prediction = Prediction.objects.create(
                user=user,
                ml_model=ml_model,
                input_source_type="csv" if csv_file else "text",
                completed_at=timezone.now()
            )

            compounds_to_fetch = []
            results = []
            smiles_set = set(smiles_list)
            existing_compounds = Compound.objects.filter(smiles__in=smiles_set)
            compound_map = {c.smiles: c for c in existing_compounds}

            for smiles, ic50 in zip(smiles_list, predictions):
                compound = compound_map.get(smiles)
                if compound:
                    results.append((smiles, ic50, compound))
                else:
                    compounds_to_fetch.append((smiles, ic50))

            fetched_compounds = {}
            if compounds_to_fetch:
                with ThreadPoolExecutor() as executor:
                    future_to_smiles = {
                        executor.submit(self.fetch_pubchem_data, smiles): (smiles, ic50)
                        for smiles, ic50 in compounds_to_fetch
                    }
                    for future in as_completed(future_to_smiles):
                        smiles, ic50 = future_to_smiles[future]
                        try:
                            fetch_data = future.result()
                            compound = Compound.objects.create(smiles=smiles, **fetch_data)
                            fetched_compounds[smiles] = (ic50, compound)
                        except Exception as e:
                            fetched_compounds[smiles] = (ic50, None)

            response_data = []
            prediction_compounds = []

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.process_prediction, smiles, ic50, compound_map.get(smiles), prediction)
                    for smiles, ic50 in zip(smiles_list, predictions)
                ]
                for future in as_completed(futures):
                    response_item, pred_comp = future.result()
                    response_data.append(response_item)
                    if pred_comp:
                        prediction_compounds.append(pred_comp)
            PredictionCompound.objects.bulk_create(prediction_compounds)

            return Response({
                "status": "success",
                "message": f"Prediction complete and saved for {len(response_data)} SMILES.",
                "data": response_data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def process_prediction(self, smiles, ic50, compound, prediction):
        if ic50 > 6:
            category = "very strong"
        elif 5 < ic50 <= 6:
            category = "strong"
        elif 4 < ic50 <= 5:
            category = "moderate"
        elif 3 < ic50 <= 4:
            category = "weak"
        else:
            category = "inactive"

        mol = Chem.MolFromSmiles(smiles)
        if mol:
            heavy_atoms = mol.GetNumHeavyAtoms()
            clogP = Crippen.MolLogP(mol)
        else:
            heavy_atoms, clogP = None, None

        le = (1.37 * ic50) / heavy_atoms if heavy_atoms and clogP else None
        lelp = clogP / le if le else None

        prediction_compound = None
        if compound:
            prediction_compound = PredictionCompound(
                compound=compound,
                ic50=ic50,
                category=category,
                prediction=prediction
            )

        response_item = {
            "smiles": smiles,
            "pic50": ic50,
            "lelp": lelp,
            "category": category,
            "compound": {
                "id": compound.id if compound else None,
                "smiles": compound.smiles if compound else smiles,
                "iupac_name": getattr(compound, "iupac_name", None),
                "cid": getattr(compound, "cid", None),
                "description": getattr(compound, "description", None),
                "molecular_formula": getattr(compound, "molecular_formula", None),
                "molecular_weight": getattr(compound, "molecular_weight", None),
                "synonyms": getattr(compound, "synonyms", None),
                "inchi": getattr(compound, "inchi", None),
                "inchikey": getattr(compound, "inchikey", None),
                "structure_image": getattr(compound, "structure_image", None)
            }
        }

        return response_item, prediction_compound

    def fetch_pubchem_data(self, smiles):
        data = {
            "cid": None, "molecular_formula": None, "molecular_weight": None,
            "iupac_name": None, "inchi": None, "inchikey": None, "description": None,
            "synonyms": None, "structure_image": None
        }

        try:
            compounds = pcp.get_compounds(smiles, 'smiles')
            if compounds:
                compound = compounds[0]
                data.update({
                    "cid": compound.cid,
                    "molecular_formula": compound.molecular_formula,
                    "molecular_weight": compound.molecular_weight,
                    "iupac_name": compound.iupac_name,
                    "inchi": compound.inchi,
                    "inchikey": compound.inchikey,
                    "synonyms": ", ".join(compound.synonyms) if compound.synonyms else None,
                    "structure_image": f"https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={compound.cid}&t=l" if compound.cid else None,
                })

                if compound.cid:
                    description = self.fetch_pubchem_description(compound.cid)
                    if description:
                        data["description"] = description
                        
        except Exception as e:
            print(f"Error fetching data from PubChem: {e}")
        return data

    def fetch_pubchem_description(self, cid):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                json_data = response.json()
                descriptions = json_data.get("InformationList", {}).get("Information", [])
                for item in descriptions:
                    if "Description" in item:
                        return item["Description"]
        except requests.RequestException as e:
            print(f"Error fetching description from PubChem: {e}")
        return None


@extend_schema(**prediction_download_schema)
class PredictionDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        try:
            prediction = Prediction.objects.get(id=id)
        except Prediction.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Prediction not found.",
                    "data": None
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if prediction.user != request.user and not getattr(request.user, "is_admin", False):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to download this prediction.",
                    "data": None
                },
                status=status.HTTP_403_FORBIDDEN
            )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="prediction_{prediction.id}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "SMILES",
            "IUPAC_Name",
            "Molecular_Formula",
            "Molecular_Weight",
            "Predicted_IC50",
            "Predicted_Category",
            "PubChem_CID",
        ])

        prediction_results = prediction.prediction_compounds.select_related("compound").all()
        for result in prediction_results:
            writer.writerow([
                result.compound.smiles,
                result.compound.iupac_name,
                result.compound.molecular_formula,
                result.compound.molecular_weight,
                result.ic50,
                result.category,
                result.compound.cid,
            ])

        return response