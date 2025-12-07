import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# Garante que todas as pastas existam
for d in [LOG_DIR, INPUT_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Configura o Log
logging.basicConfig(
    filename=LOG_DIR / 'processamento.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class ExcelPipeline:
    def __init__(self, input_dir=None, output_dir=None):
        self.input_path = Path(input_dir) if input_dir else INPUT_DIR
        self.output_path = Path(output_dir) if output_dir else OUTPUT_DIR
        
        # --- SEU MAPA DE COLUNAS (Mantido da versão anterior) ---
        self.schema_map = {
            'Vendedor': 'cliente',
            'Valor': 'valor_venda',
            'Data': 'data_venda',
            'Custo': 'custo'
        }

    def ingest_files(self):
        """Lê arquivos da pasta de input."""
        if not self.input_path.exists(): return pd.DataFrame()

        files = list(self.input_path.glob('*'))
        all_data = []

        for file in files:
            try:
                if file.name.startswith('~$'): continue
                
                if file.suffix == '.xlsx':
                    df = pd.read_excel(file, engine='openpyxl')
                elif file.suffix == '.csv':
                    df = pd.read_csv(file)
                else:
                    continue
                
                df['source_file'] = file.name
                all_data.append(df)
            except Exception as e:
                logging.error(f"Erro ao ler {file.name}: {e}")

        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

    def clean_and_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df

        # Renomear
        df = df.rename(columns=self.schema_map)
        
        # Limpar texto
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Converter Números
        if 'valor_venda' in df.columns:
            df['valor_venda'] = pd.to_numeric(df['valor_venda'], errors='coerce').fillna(0.0)
        
        if 'custo' in df.columns:
            df['custo'] = pd.to_numeric(df['custo'], errors='coerce').fillna(0.0)
        
        # Converter Datas
        if 'data_venda' in df.columns:
            df['data_venda'] = pd.to_datetime(df['data_venda'], errors='coerce')

        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df

        if 'valor_venda' in df.columns and 'custo' in df.columns:
            df['margem_lucro'] = df['valor_venda'] - df['custo']
            df['margem_percentual'] = df.apply(
                lambda x: (x['margem_lucro'] / x['valor_venda']) if x['valor_venda'] != 0 else 0, 
                axis=1
            ).round(4)
        return df

    def validate(self, df: pd.DataFrame):
        if df.empty: return
        if 'valor_venda' in df.columns:
            inconsistent = df[df['valor_venda'] < 0]
            if not inconsistent.empty:
                inconsistent.to_csv(self.output_path / 'erros_validacao.csv', index=False, sep=';')

    def generate_diffs(self, current_df: pd.DataFrame):
        """
        Compara o arquivo atual com o último processado para achar novos registros.
        """
        try:
            # Busca o último parquet gerado
            parquet_files = sorted(self.output_path.glob("consolidado_*.parquet"))
            
            if not parquet_files:
                logging.info("Primeira execução: Sem histórico para comparar.")
                return None

            last_file = parquet_files[-1]
            logging.info(f"Comparando com versão anterior: {last_file.name}")
            
            old_df = pd.read_parquet(last_file)

            # Compara os dois DataFrames
            # indicator=True cria uma coluna `_merge` dizendo se a linha é nova ou velha
            diff_df = pd.merge(current_df, old_df, how='outer', indicator=True)
            
            # Filtra apenas o que está no 'left_only' (apenas no arquivo novo)
            new_entries = diff_df[diff_df['_merge'] == 'left_only']
            
            if not new_entries.empty:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                diff_path = self.output_path / f"DIFF_novos_registros_{timestamp}.csv"
                
                # Salva o arquivo de diferenças
                new_entries.drop(columns=['_merge']).to_csv(diff_path, index=False, sep=';', decimal=',')
                logging.info(f"Diff gerado com {len(new_entries)} novas linhas.")
                return diff_path
            
            return None

        except Exception as e:
            logging.error(f"Erro na geração de diffs: {e}")
            return None

    def export(self, df: pd.DataFrame):
        if df.empty: return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            df.to_parquet(self.output_path / f"consolidado_{timestamp}.parquet", engine='pyarrow')
            df.to_csv(self.output_path / f"consolidado_{timestamp}.csv", index=False, sep=';', decimal=',')
            logging.info(f"Arquivos salvos com sucesso: {timestamp}")
        except Exception as e:
            logging.error(f"Erro ao exportar: {e}")

    def run(self):
        logging.info(">>> JOB INICIADO <<<")
        raw = self.ingest_files()
        if raw.empty: return
        
        clean = self.clean_and_normalize(raw)
        final = self.transform(clean)
        self.validate(final)
        self.generate_diffs(final)
        self.export(final)
        logging.info(">>> JOB FINALIZADO <<<")