import requests
from datetime import datetime

def programar_inspeccion():
    center_id = input("Ingrese la ID del Centro: ")
    module_id = input("Ingrese la ID del modulo: ")
    target_date_input = input("Ingrese Fecha de ejecucion (YYYY-MM-DD): ")
    inspection_type = input("Ingrese tipo de operacion (1 = Video o 2 = Sonar): ")
    manager_id = input("Ingrese la ID su ID (integer): ")
    unit_id = int(input("Ingrese la ID de la Unidad: "))

    

    try:
        date_obj = datetime.strptime(target_date_input, "%Y-%m-%d")
        target_date = date_obj.isoformat() + "Z"  
    except ValueError:
        print("Error: La fecha debe estar en formato YYYY-MM-DD.")
        return
    

    data = {
        "centerId": center_id,
        "moduleId": module_id,
        "targetDate": target_date,
        "type": inspection_type,
        "managerId": manager_id,
        "unitId": unit_id
    }
    

    url = "http://localhost:3000/api/programmed-inspection/"
    try:
        response = requests.post(url, json=data)
        json_response = response.json()
        
        if response.status_code == 201:
            print(json_response['message'])
            return True
        elif response.status_code == 400:
            print(json_response['message'])
        elif response.status_code == 404:
            print(json_response['message'])
        else:
            print(json_response['message'])
        
        return False
    
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return False


if __name__ == "__main__":
    programar_inspeccion() 