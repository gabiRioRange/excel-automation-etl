from src.pipeline import ExcelPipeline
import os

def main():
    # Caminhos relativos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_DIR = os.path.join(BASE_DIR, 'data', 'input')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'output')
    
    # Garante que as pastas existam
    os.makedirs(INPUT_DIR, exist_ok=True)
    
    print("🚀 Iniciando Automação de Excel...")
    
    automator = ExcelPipeline(INPUT_DIR, OUTPUT_DIR)
    automator.run()
    
    print("✅ Processamento concluído! Verifique a pasta data/output e logs.")

if __name__ == "__main__":
    main()