import requests
import os
from datetime import datetime

def login():
    url = "http://localhost:3000/api/auth/callback/credentials"
    
    email = input("Ingrese su email: ")
    password = input("Ingrese su contraseña: ")
    
    data = {
        "email": email,
        "password": password,
        "redirect": "false",
        "callbackUrl": "http://localhost:3000"
    }
    
    session = requests.Session()
    
    try:
        csrf_response = session.get("http://localhost:3000/api/auth/csrf")
        csrf_data = csrf_response.json()
        csrf_token = csrf_data.get("csrfToken", "")
        
        if csrf_token:
            data["csrfToken"] = csrf_token
        
        response = session.post(url, data=data, allow_redirects=False)

        if response.status_code == 200 or response.status_code == 302:

            if "error" in response.text.lower() or "invalid" in response.text.lower():
                print("Error de autenticación: Credenciales no válidas")
                return None
            else:
                verify_response = session.get("http://localhost:3000/api/auth/session")
                user_data = verify_response.json()
                if user_data and user_data.get("user"):
                    print("Login exitoso y verificado")
                    return session
                else:
                    print("Login falló en la verificación")
                    return None
        else:
            print(f"Error de autenticación: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

def logout(session):
    url = "http://localhost:3000/api/auth/signout"
    
    try:
        csrf_response = session.get("http://localhost:3000/api/auth/csrf")
        csrf_data = csrf_response.json()
        csrf_token = csrf_data.get("csrfToken", "")
        
        data = {"csrfToken": csrf_token} if csrf_token else {}
        
        response = session.post(url, data=data)
        
        if response.status_code == 200:
            print("Sesión cerrada exitosamente")
            return True
        else:
            print(f"Error al cerrar sesión: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al cerrar sesión: {e}")
        return False

def ejecutar_inspeccion(session):
    video_path = input("Ingrese la ruta del archivo de video: ")
    nombre_operacion = input("Ingrese el nombre de la operación: ")
    frame_interval = input("Ingrese el intervalo de frames: ") or "1"
    

    try:
        user_info_response = session.get("http://localhost:3000/api/auth/session")
        user_data = user_info_response.json()
        user_id = user_data.get("user", {}).get("id", "")
        if not user_id:
            print("No se pudo obtener el ID del usuario")
            logout(session);
            return False
    except Exception as e:
        print(f"Error al obtener información del usuario: {e}")
        logout(session);
        return False
    

    if not os.path.isfile(video_path):
        print(f"Error: El archivo {video_path} no existe")
        logout(session);
        return False
    

    API_URL = "http://localhost:8001" 
    
    files = {
        'upload_file': (os.path.basename(video_path), open(video_path, 'rb'), 'video/mp4')
    }
    
    data = {
        'userId': user_id,
        'video_duration': '1',
        'other_data1': '',
        'other_data2': ''
    }
    
    try:
        print("Subiendo video...")
        upload_response = session.post(f"{API_URL}/api/v1/video", 
                                    headers={'accept': 'application/json'},
                                    files=files,
                                    data=data)
        
        if upload_response.status_code != 200:
            print(f"Error al subir el video: {upload_response.status_code}")
            print(upload_response.text)
            logout(session);
            return False
        
        upload_data = upload_response.json()
        video_id = upload_data.get("video_id")
        video_url = upload_data.get("video_url")
        
        if not video_id:
            print("No se pudo obtener el ID del video")
            logout(session);
            return False
        
        print(f"Video subido con éxito. ID: {video_id}, URL: {video_url}")
        

        request_data = {
            "video_id": video_id,
            "name": nombre_operacion,
            "task_model": "demo", 
            "frame_interval": int(frame_interval)
        }
        
        print("Solicitando procesamiento del video...")
        process_response = session.post(f"{API_URL}/api/v1/video_request",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'accept': 'application/json'
                                     },
                                     json=request_data)
        
        if process_response.status_code != 200:
            print(f"Error al solicitar el procesamiento: {process_response.status_code}")
            print(process_response.text)
            logout(session);
            return False
        
        process_data = process_response.json()
        process_id = process_data.get("process_id")
        
        print(f"Inspección iniciada con éxito. ID del proceso: {process_id}")
        print(f"Puedes ver los resultados en: http://localhost:3000/demo/reports/{process_id}")
        
        return True
        
    except Exception as e:
        print(f"Error durante la ejecución de la inspección: {e}")
        logout(session);
        return False
    finally:

        if 'upload_file' in files and hasattr(files['upload_file'][1], 'close'):
            files['upload_file'][1].close()

if __name__ == "__main__":

    session = login()
    
    if session:
        result = ejecutar_inspeccion(session)
        logout(session)
        
        if result:
            print("Proceso completado con éxito.")
        else:
            print("No se pudo completar la ejecución de la inspección.")
    else:
        print("No se pudo completar la autenticación. No es posible ejecutar la inspección.")