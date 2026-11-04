"""
Σ-FDL::FUTURE-CALC v3.0
COMPLEX-PHASE / UNIVERSAL WAVE ARCHITECTURE

Реализация предоставленной формулы.
Неопределённые в исходной спецификации операторы (K_vac, epsilon,
переход 000->111 и коэффициенты) передаются извне, без выдумывания
их математического смысла.

Требуется Python 3.10+.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping
import cmath
import math


Complex = complex
Scalar = float | int | complex
StateFunction = Callable[[Any], Scalar]
EpsilonFunction = Callable[[Complex], Scalar]
TransitionFunction = Callable[[], Scalar]


class ModelDomainError(ValueError):
    """Ошибка области определения или численной устойчивости модели."""


@dataclass(frozen=True)
class PhaseParameters:
    omega: float
    alpha: float
    delta: float
    omega_L: float

    def validate(self) -> None:
        values = {
            "omega": self.omega,
            "alpha": self.alpha,
            "delta": self.delta,
            "omega_L": self.omega_L,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ModelDomainError(f"{name} должен быть конечным числом.")


@dataclass(frozen=True)
class WaveCoefficients:
    """
    Коэффициенты формулы.

    coeff_e23 соответствует e_23 * 333.
    coeff_e2_78 соответствует e^2_78 * 888.
    feigenbaum соответствует Фейг * 666.
    """
    phi_12: Scalar
    coeff_e23: Scalar
    alpha_k34: Scalar
    feigenbaum: Scalar
    g_67: Scalar
    coeff_e2_78: Scalar
    r_89: Scalar

    def as_dict(self) -> dict[str, Scalar]:
        return {
            "phi_12": self.phi_12,
            "coeff_e23": self.coeff_e23,
            "alpha_k34": self.alpha_k34,
            "feigenbaum": self.feigenbaum,
            "g_67": self.g_67,
            "coeff_e2_78": self.coeff_e2_78,
            "r_89": self.r_89,
        }


@dataclass
class SigmaFDLConfig:
    phase: PhaseParameters
    coefficients: WaveCoefficients

    # K_vac(S): пользовательская функция состояния вакуумного контура.
    k_vac: StateFunction

    # epsilon(Sigma): внешний оператор согласования/нормировки.
    # На вход получает сумму волновых слагаемых до умножения на epsilon.
    epsilon: EpsilonFunction

    # arcsin(000 -> 111): передаётся числовой аргумент arcsin
    # либо функция, возвращающая этот аргумент.
    transition_000_111: Scalar | TransitionFunction

    # Числовая точность проверки знаменателей.
    singularity_tolerance: float = 1e-12


@dataclass
class WaveResult:
    time: float
    state: Any
    z_theta: Complex
    real_phase: float
    imaginary_phase: float
    terms: dict[str, Complex]
    subtotal: Complex
    epsilon_value: Complex
    sigma_universe: Complex

    def as_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "z_theta": self.z_theta,
            "real_phase": self.real_phase,
            "imaginary_phase": self.imaginary_phase,
            "terms": self.terms,
            "subtotal": self.subtotal,
            "epsilon": self.epsilon_value,
            "sigma_universe": self.sigma_universe,
        }


class SigmaFDLFutureCalc:
    """
    Вычислительное ядро Σ-FDL::FUTURE-CALC v3.0.

    Реализует:
      1. Z_theta(t) = (omega*t + alpha)
                     + i*delta*omega_L*(1 - K_vac(S))
      2. Полную сумму Σ-Вселенной(t).
      3. Внешнее умножение на epsilon(Sigma).
      4. Возвращает разложение результата по слагаемым.
    """

    def __init__(self, config: SigmaFDLConfig):
        self.config = config
        self.config.phase.validate()

        if self.config.singularity_tolerance <= 0:
            raise ModelDomainError("singularity_tolerance должна быть > 0.")

    @staticmethod
    def _as_complex(value: Scalar, name: str) -> Complex:
        try:
            result = complex(value)
        except (TypeError, ValueError) as exc:
            raise ModelDomainError(f"{name}: значение не является числом.") from exc

        if not (math.isfinite(result.real) and math.isfinite(result.imag)):
            raise ModelDomainError(f"{name}: значение должно быть конечным.")
        return result

    def phase_argument(self, t: float, state: Any) -> Complex:
        """Вычисляет комплексный аргумент фазы Z_theta(t)."""
        if not math.isfinite(t):
            raise ModelDomainError("Время t должно быть конечным числом.")

        p = self.config.phase
        k_vac = self._as_complex(self.config.k_vac(state), "K_vac(S)")

        real_part = p.omega * t + p.alpha
        imag_part = p.delta * p.omega_L * (1 - k_vac)

        return complex(real_part, 0) + 1j * imag_part

    def _transition_argument(self) -> Complex:
        raw = self.config.transition_000_111
        value = raw() if callable(raw) else raw
        z = self._as_complex(value, "аргумент arcsin(000->111)")

        # Комплексный arcsin допустим; здесь не ограничиваем аргумент [-1, 1].
        return z

    def _safe_reciprocal(
        self, value: Complex, function_name: str
    ) -> Complex:
        tol = self.config.singularity_tolerance
        if abs(value) <= tol:
            raise ModelDomainError(
                f"Сингулярность в {function_name}: знаменатель близок к нулю."
            )
        return 1 / value

    def calculate(self, t: float, state: Any) -> WaveResult:
        z = self.phase_argument(t, state)
        c = self.config.coefficients

        sin_z = cmath.sin(z)
        cos_z = cmath.cos(z)

        # Тригонометрические функции комплексного аргумента.
        tan_z = self._safe_reciprocal(cos_z, "tg(Z_theta)") * sin_z
        sec_z = self._safe_reciprocal(cos_z, "sec(Z_theta)")
        cot_z = self._safe_reciprocal(sin_z, "ctg(Z_theta)") * cos_z
        csc_z = self._safe_reciprocal(sin_z, "cosec(Z_theta)")

        transition = cmath.asin(self._transition_argument())

        # Слагаемые записаны отдельно, чтобы сохранять трассируемость формулы.
        terms: dict[str, Complex] = {
            "000": complex(0, 0),
            "arcsin(000->111)": transition,
            "111*cos(Z_theta)": 111 * cos_z,
            "phi_12*222": self._as_complex(c.phi_12, "phi_12") * 222,
            "e_23*333": self._as_complex(c.coeff_e23, "coeff_e23") * 333,
            "337*cos(Z_theta)": 337 * cos_z,
            "alpha_K34*444": self._as_complex(c.alpha_k34, "alpha_k34") * 444,
            "pi*555": math.pi * 555,
            "Feig*666": self._as_complex(c.feigenbaum, "feigenbaum") * 666,
            "666*sin(Z_theta)": 666 * sin_z,
            "G_67*674*tg(Z_theta)": (
                self._as_complex(c.g_67, "g_67") * 674 * tan_z
            ),
            "777*sec(Z_theta)": 777 * sec_z,
            "e2_78*888*ctg(Z_theta)": (
                self._as_complex(c.coeff_e2_78, "coeff_e2_78") * 888 * cot_z
            ),
            "R_89*999*cosec(Z_theta)": (
                self._as_complex(c.r_89, "r_89") * 999 * csc_z
            ),
        }

        subtotal = sum(terms.values(), 0j)
        epsilon_value = self._as_complex(
            self.config.epsilon(subtotal), "epsilon(Sigma)"
        )
        sigma_universe = subtotal * epsilon_value

        return WaveResult(
            time=t,
            state=state,
            z_theta=z,
            real_phase=z.real,
            imaginary_phase=z.imag,
            terms=terms,
            subtotal=subtotal,
            epsilon_value=epsilon_value,
            sigma_universe=sigma_universe,
        )

    def calculate_series(
        self, times: list[float], state: Any
    ) -> list[WaveResult]:
        """Вычисляет временной ряд для одного заданного состояния S."""
        return [self.calculate(t, state) for t in times]


# ---------------------------------------------------------------------
# 22-ступенчатый контур «Акта Творения»
# ---------------------------------------------------------------------
# Этапы намеренно представлены как входные записи. Их содержательные
# вычислители должны быть определены спецификацией проекта, а не придуманы
# внутри этого математического ядра.

ACT_OF_CREATION_22 = {
    1: "Возникновение замысла",
    2: "Осознание внутреннего импульса",
    3: "Формулирование замысла",
    4: "Определение исходных условий и среды",
    5: "Формирование общей концепции",
    6: "Определение целей",
    7: "Выделение зон интереса",
    8: "Определение связей и ресурсов",
    9: "Формирование числовых индексов",
    10: "Определение направлений",
    11: "Выявление потребностей",
    12: "Классификация потребностей",
    13: "Определение типов средств",
    14: "Выбор средств",
    15: "Интуитивный фильтр / MetaHarmony",
    16: "Приоритетный курс KP",
    17: "Определение узлов деятельности",
    18: "Формирование программ и обратной связи",
    19: "Критерии и значимость показателей",
    20: "Затраты, эффективность и признание",
    21: "Знаковая модель M",
    22: "Запуск и воплощение Уп",
}


@dataclass
class ActOfCreationRecord:
    """Заполненные значения 22 ступеней; пустые значения допустимы."""
    values: dict[int, Any] = field(default_factory=dict)

    def set_step(self, step: int, value: Any) -> None:
        if step not in ACT_OF_CREATION_22:
            raise KeyError(f"Ступень должна находиться в диапазоне 1..22: {step}")
        self.values[step] = value

    def report(self) -> list[dict[str, Any]]:
        return [
            {
                "step": number,
                "name": name,
                "value": self.values.get(number),
                "filled": number in self.values,
            }
            for number, name in ACT_OF_CREATION_22.items()
        ]


def example_configuration() -> SigmaFDLConfig:
    """
    Демонстрационная конфигурация интерфейса, НЕ калибровка модели.

    Числа ниже — нейтральные тестовые значения. Перед исследовательским
    применением замените их на параметры, определённые вашей методикой.
    """
    return SigmaFDLConfig(
        phase=PhaseParameters(
            omega=1.0,
            alpha=0.0,
            delta=1.0,
            omega_L=1.0,
        ),
        coefficients=WaveCoefficients(
            phi_12=1.0,
            coeff_e23=1.0,
            alpha_k34=1.0,
            feigenbaum=1.0,
            g_67=1.0,
            coeff_e2_78=1.0,
            r_89=1.0,
        ),
        k_vac=lambda state: state["K_vac"],
        epsilon=lambda subtotal: 1.0,
        transition_000_111=0.5,
    )


if __name__ == "__main__":
    # Демонстрационный запуск.
    # K_vac и epsilon здесь заданы только для проверки программного контура.
    model = SigmaFDLFutureCalc(example_configuration())

    sample_state = {"K_vac": 0.25}
    result = model.calculate(t=1.0, state=sample_state)

    print("Σ-FDL::FUTURE-CALC v3.0")
    print("Z_theta =", result.z_theta)
    print("Subtotal =", result.subtotal)
    print("epsilon =", result.epsilon_value)
    print("Sigma-Universe =", result.sigma_universe)
    print("\nРазложение:")
    for term_name, term_value in result.terms.items():
        print(f"  {term_name:32s} = {term_value}")
