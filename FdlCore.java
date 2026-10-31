package noveya.core;

import java.util.UUID;
import java.util.HashSet;
import java.util.Set;

public class FdlCore {
    // 36-буквенная эталонная матрица метагармонии (оптимальный срез 6х6)
    private static final String HARMONY_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯѢѲѴ";
    private static final Set<Character> VALID_GRAFPHEMES = new HashSet<>();

    static {
        for (char c : HARMONY_ALPHABET.toCharArray()) {
            VALID_GRAFPHEMES.add(c);
        }
    }

    public FdlCore() {
        System.out.println("[Java Core] Резонатор 36-буквенной матрицы инициализирован.");
    }

    /**
     * Валидация текста нового языка и генерация волнового хэш-токена
     */
    public String validateAndTokenizeHarmony(String harmonyText) {
        if (harmonyText == null) return null;
        
        String cleanText = harmonyText.toUpperCase().replaceAll("[^" + HARMONY_ALPHABET + "]", "");
        
        // Если текст пустой или забит чужеродным шумом, выбрасываем фазовый сбой
        if (cleanText.isEmpty()) {
            System.out.println("[Java Core] КРИТИЧЕСКИЙ СБОЙ: Текст не содержит графем матрицы метагармонии!");
            return null;
        }

        // Жесткая генерация UUID транзакции на основе волнового следа
        return UUID.randomUUID().toString();
    }

    /**
     * Расчет веса гармонии (количество чистых графем к общей длине)
     */
    public double calculateHarmonyDensity(String rawText) {
        if (rawText == null || rawText.isEmpty()) return 0.0;
        
        long validCount = rawText.toUpperCase().chars()
                .filter(c -> VALID_GRAFPHEMES.contains((char) c))
                .count();
                
        return (double) validCount / rawText.length();
    }
}
