import os
import subprocess
import jpype
import jpype.imports
from jpype.types import *

class FdlBridgeCompiler:
    def __init__(self, java_src_dir="./src", output_dir="./bin"):
        self.java_src_dir = java_src_dir
        self.output_dir = output_dir
        
        # Создаем директории, если их нет
        os.makedirs(java_src_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

    def compile_java_core(self):
        """Автоматическая компиляция Java-кода в байт-код (.class)"""
        print("[Compiler] Сборка формального Java-каркаса...")
        java_file_path = os.path.join(self.java_src_dir, "FdlCore.java")
        
        # Компилируем через стандартный javac
        compile_cmd = ["javac", "-d", self.output_dir, java_file_path]
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Ошибка компиляции Java: {result.stderr}")
        print("[Compiler] Java-байт-код успешно собран в папку bin/")

    def start_symbiosis(self):
        """Запуск JVM и склейка сред в едином адресном пространстве памяти"""
        if not jpype.isJVMStarted():
            print("[Bridge] Запуск JVM. Общая память активирована.")
            # Добавляем скомпилированный bin/ в ClassPath Явы
            jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={self.output_dir}")
        
        # Импортируем скомпилированный класс напрямую в Python-инфосферу
        from noveya.core import FdlCore
        
        print("[Bridge] Склейка завершена. Python (Образный UI) <-> Java (Формальное Ядро).")
        return FdlCore()

# ==========================================
# ДЕМОНСТРАЦИЯ РАБОТЫ ЖИВОЙ МОДЕЛИ (СИМБИОЗ)
# ==========================================
if __name__ == "__main__":
    # 1. Инициализируем компилятор
    compiler = FdlBridgeCompiler(java_src_dir="./noveya/core", output_dir="./bin")
    
    # В реальной системе этот файл уже лежит на диске, создаем его для теста
    java_code = """package noveya.core;
public class FdlCore {
    public boolean executeSynthesis(String t, String a) {
        System.out.println("[Java Engine] Снятие дискретности меридианов: " + t + " <-> " + a);
        return true;
    }
}"""
    os.makedirs("./noveya/core", exist_ok=True)
    with open("./noveya/core/FdlCore.java", "w", encoding="utf-8") as f:
        f.write(java_code)

    # 2. Компилируем Java из Python
    compiler.compile_java_core()

    # 3. Активируем мост симбиоза
    java_core_instance = compiler.start_symbiosis()

    # 4. Прямое диалектическое взаимодействие:
    # Передаем гибкие образы Python напрямую в строгий исполняющий метод Java
    python_thesis = "Николаев — сотовый каркас Света"
    python_antithesis = "Старые догмы внешнего управления"

    # Вызов метода Java из Python идет напрямую, без прослоек
    success = java_core_instance.executeSynthesis(python_thesis, python_antithesis)
    
    if success:
        print("[Python UI] Результат валидирован. Состояние: SALAM (\u03a3 = 0)")
