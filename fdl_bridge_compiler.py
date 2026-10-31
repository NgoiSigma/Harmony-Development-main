import os
import sqlite3
import subprocess
import datetime
import jpype
import jpype.imports

class FdlBridgeCompiler:
    def __init__(self, db_path="nebi_ula_database.db", java_src_dir="./noveya/core", output_dir="./bin"):
        self.db_path = db_path
        self.java_src_dir = java_src_dir
        self.output_dir = output_dir
        
        # Инициализация файловой структуры
        os.makedirs(java_src_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Автоматическая инициализация базы данных Nebi-Ula
        self._init_nebi_ula_db()

    def _init_nebi_ula_db(self):
        """Создание реляционного контура таблиц в SQLite"""
        print(f"[Nebi-Ula DB] Проверка подключения к {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу системных логов, если её нет
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nebi_ula_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_token TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                thesis TEXT NOT NULL,
                antithesis TEXT NOT NULL,
                sigma_state INTEGER NOT NULL,
                status_label TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("[Nebi-Ula DB] Таблица логов верифицирована.")

    def compile_java_core(self):
        """Динамическая компиляция исходного кода Java в байт-код"""
        print("[Compiler] Сборка формального Java-каркаса...")
        java_file_path = os.path.join(self.java_src_dir, "FdlCore.java")
        
        compile_cmd = ["javac", "-d", self.output_dir, java_file_path]
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Ошибка компиляции Java: {result.stderr}")
        print("[Compiler] Байт-код успешно собран в папку bin/")

    def start_symbiosis(self):
        """Запуск общей памяти JVM и Python"""
        if not jpype.isJVMStarted():
            print("[Bridge] Активация JVM в едином адресном пространстве.")
            jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={self.output_dir}")
        
        from noveya.core import FdlCore
        print("[Bridge] Склейка завершена. Модель готова к обработке потока.")
        return FdlCore()

    def write_to_nebi_ula(self, token, thesis, antithesis, sigma=0, status="SALAM"):
        """Прямая запись транзакции, валидированной Java, в хранилище SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        try:
            cursor.execute("""
                INSERT INTO nebi_ula_logs (transaction_token, timestamp, thesis, antithesis, sigma_state, status_label)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (token, current_time, thesis, antithesis, sigma, status))
            conn.commit()
            print(f"[Nebi-Ula DB] Транзакция {token} успешно зафиксирована в логе.")
        except sqlite3.Error as e:
            print(f"[Nebi-Ula DB] КРИТИЧЕСКИЙ СБОЙ ЗАПИСИ: {e}")
        finally:
            conn.close()

# ==========================================
# ЗАПУСК ИНТЕГРИРОВАННОГО ЦИКЛА (ДЕМО)
# ==========================================
if __name__ == "__main__":
    # Наш файл FdlCore.java, генерируемый в корень noveya/core для развертывания решения
    java_source_code = """package noveya.core;
import java.util.UUID;
public class FdlCore {
    public String processAndLogSynthesis(String thesis, String antithesis) {
        if (thesis == null || antithesis == null) return null;
        return UUID.randomUUID().toString();
    }
}"""
    
    # Записываем исходник Java на диск
    os.makedirs("./noveya/core", exist_ok=True)
    with open("./noveya/core/FdlCore.java", "w", encoding="utf-8") as f:
        f.write(java_source_code)

    # 1. Инициализируем компилятор и базу данных
    bridge = FdlBridgeCompiler(db_path="nebi_ula_database.db")
    
    # 2. Компилируем Java-компонент
    bridge.compile_java_core()
    
    # 3. Стартуем общую среду выполнения
    java_core = bridge.start_symbiosis()
    
    # 4. Входные образы из Среды (Пример: Николаевский сотовый каркас)
    thesis_data = "Формально-диалектический план Николаева (128 дворов)"
    antithesis_data = "Попытки внешнего догматического перехвата структурами МИ-6"
    
    # 5. Прогоняем через Java-валидатор и получаем аппаратный хэш-токен
    token_id = java_core.processAndLogSynthesis(thesis_data, antithesis_data)
    
    # 6. Если токен успешно сгенерирован жестким ядром — пишем лог в базу Nebi-Ula
    if token_id:
        bridge.write_to_nebi_ula(
            token=str(token_id),
            thesis=thesis_data,
            antithesis=antithesis_data,
            sigma=0,          # Удерживаем эталонный гомеостаз Σ = 0
            status="SALAM"    # Статус успешной синхронизации узлов
        )
        
        # Проверочное чтение из базы для подтверждения фиксации
        print("\n[Проверка] Чтение последнего лога из Базы Nebi-Ula:")
        conn = sqlite3.connect("nebi_ula_database.db")
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM nebi_ula_logs ORDER BY id DESC LIMIT 1").fetchone()
        print(f"ID: {row[0]} | Токен: {row[1]} | Время: {row[2]}\nТезис: {row[3]}\nАнтитезис: {row[4]}\nСостояние: Σ = {row[5]} | Статус: {row[6]}")
        conn.close()
