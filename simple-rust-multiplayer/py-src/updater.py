import aiohttp
import asyncio
import os
import sys
import json
import zipfile
import shutil
from tqdm import tqdm
from constants import CURRENT_VERSION, UPDATE_URL

async def check_for_updates():
    print(f"[Updater] Versione corrente: {CURRENT_VERSION}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(UPDATE_URL, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    remote_version = data.get("version")
                    update_url = data.get("url")
                    
                    if remote_version and remote_version > CURRENT_VERSION:
                        print(f"[Updater] Nuova versione trovata: {remote_version}")
                        return update_url
                    else:
                        print("[Updater] L'app è aggiornata.")
                else:
                    print(f"[Updater] Impossibile verificare aggiornamenti (Status: {resp.status})")
    except Exception as e:
        print(f"[Updater] Errore durante il controllo aggiornamenti: {e}")
    return None

async def download_update(url, dest):
    print(f"[Updater] Download in corso da {url}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"[Updater] Errore download: {resp.status}")
                    return False
                    
                total = int(resp.headers.get('content-length', 0))
                with open(dest, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True, desc="Scaricamento") as pbar:
                    async for chunk in resp.content.iter_chunked(1024):
                        f.write(chunk)
                        pbar.update(len(chunk))
        return True
    except Exception as e:
        print(f"[Updater] Errore durante il download: {e}")
        return False

def apply_update(zip_path):
    print("[Updater] Applicazione aggiornamento...")
    tmp_dir = "tmp_update"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        # Sostituzione file
        # Otteniamo la cartella dove si trova lo script corrente
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                src_path = os.path.join(root, file)
                # Calcoliamo il percorso relativo rispetto alla cartella temporanea
                rel_path = os.path.relpath(src_path, tmp_dir)
                dest_path = os.path.join(base_dir, rel_path)
                
                # Creiamo le cartelle di destinazione se non esistono
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Sostituiamo il file
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(src_path, dest_path)
        
        print("[Updater] Aggiornamento completato con successo.")
        return True
    except Exception as e:
        print(f"[Updater] Errore durante l'applicazione: {e}")
        return False
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)

def restart_app():
    print("[Updater] Riavvio dell'applicazione...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

async def run_updater():
    update_url = await check_for_updates()
    if not update_url:
        print("[Updater] Nessun aggiornamento da applicare.")
        return

    zip_name = "update.zip"
    success = await download_update(update_url, zip_name)
    if not success:
        print("[Updater] Download fallito.")
        return

    if not apply_update(zip_name):
        print("[Updater] Fallito il rimpiazzo dei file.")
        return

    restart_app()

if __name__ == "__main__":
    asyncio.run(run_updater())
