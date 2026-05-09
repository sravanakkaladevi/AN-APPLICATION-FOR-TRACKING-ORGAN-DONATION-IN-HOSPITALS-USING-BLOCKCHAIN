from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from ..blockchain_service import register_donor, get_donor, verify_transaction

@csrf_exempt
def api_register_donor(request):
    """API endpoint to register a donor on the blockchain."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            organ_type = data.get('organ_type')
            hospital_id = data.get('hospital_id')

            if not all([name, organ_type, hospital_id]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            result = register_donor(name, organ_type, hospital_id)
            if "error" in result:
                return JsonResponse(result, status=500)
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def api_get_donor(request):
    """API endpoint to get donor details from the blockchain."""
    donor_id = request.GET.get('id')
    if not donor_id:
        return JsonResponse({"error": "Donor ID required"}, status=400)
    
    result = get_donor(donor_id)
    if "error" in result:
        return JsonResponse(result, status=500)
    return JsonResponse(result)

def api_verify_transaction(request):
    """API endpoint to verify a transaction hash."""
    tx_hash = request.GET.get('hash')
    if not tx_hash:
        return JsonResponse({"error": "Transaction hash required"}, status=400)
    
    result = verify_transaction(tx_hash)
    if "error" in result:
        return JsonResponse(result, status=500)
    return JsonResponse(result)
