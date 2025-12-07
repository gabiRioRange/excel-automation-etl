from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
from pathlib import Path
from src.pipeline import ExcelPipeline

app = FastAPI(title="Excel Automation ETL", version="2.0")

# Caminhos
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Garante pastas
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/processar/")
async def processar_arquivo(file: UploadFile = File(...)):
    """
    Recebe um Excel, processa e retorna:
    1. O relatório de DIFERENÇAS (se houver novos dados).
    2. Ou o arquivo consolidado completo (se for a primeira vez).
    """
    # 1. Salva o arquivo temporariamente
    file_location = INPUT_DIR / file.filename
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar upload: {e}")

    # 2. Roda o Pipeline
    try:
        pipeline = ExcelPipeline(INPUT_DIR, OUTPUT_DIR)
        
        # Executa passo a passo para controlarmos o retorno
        raw_df = pipeline.ingest_files()
        if raw_df.empty:
            raise HTTPException(400, "O arquivo enviado está vazio ou ilegível.")
        
        clean_df = pipeline.clean_and_normalize(raw_df)
        final_df = pipeline.transform(clean_df)
        pipeline.validate(final_df)
        
        # Gera Diff e Exporta
        diff_file_path = pipeline.generate_diffs(final_df)
        pipeline.export(final_df)

    except Exception as e:
        raise HTTPException(500, f"Erro interno no Pipeline: {e}")
    finally:
        # Limpeza: remove o arquivo de input para não duplicar na próxima
        if file_location.exists():
            os.remove(file_location)

    # 3. Decide o que retornar ao usuário
    # Se gerou um arquivo de diferenças, retorna ele (é mais importante)
    if diff_file_path and diff_file_path.exists():
        return FileResponse(
            diff_file_path, 
            media_type='text/csv', 
            filename=f"DIFF_{file.filename}.csv"
        )
    
    # Se não, retorna o último consolidado gerado
    try:
        latest_csv = sorted(OUTPUT_DIR.glob("consolidado_*.csv"))[-1]
        return FileResponse(
            latest_csv, 
            media_type='text/csv', 
            filename="resultado_processado.csv"
        )
    except IndexError:
        return {"message": "Processamento concluído, mas nenhum arquivo de saída foi gerado."}