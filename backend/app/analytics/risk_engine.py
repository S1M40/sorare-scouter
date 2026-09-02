from typing import List, Optional, Tuple
from app.schemas.common import RiskLevelEnum, SourceTypeEnum
from app.schemas.metric import RiskFactor


def evaluate_risks(
    is_injured: bool = False,
    injury_kind: Optional[str] = None,
    injury_status: Optional[str] = None,
    is_suspended: bool = False,
    suspension_reason: Optional[str] = None,
    minutes_score: float = 80.0,
    starting_prob: float = 75.0,
    form_score: float = 60.0,
    fixture_score: float = 50.0,
    price_change_7d: Optional[float] = 0.0,
) -> Tuple[float, RiskLevelEnum, List[RiskFactor]]:
    """Evaluate multidimensional risk signals and return total risk score, level, and individual factors."""
    factors: List[RiskFactor] = []
    risk_points = 0.0

    # 1. Suspensions
    if is_suspended:
        risk_points += 60.0
        factors.append(
            RiskFactor(
                category="Discipline",
                severity=RiskLevelEnum.CRITICAL,
                message=f"Serving suspension: {suspension_reason or 'Disciplinary sanction'}",
                source_type=SourceTypeEnum.FACT,
            )
        )

    # 2. Injuries
    if is_injured:
        status = (injury_status or "OUT").upper()
        if status == "OUT":
            risk_points += 55.0
            factors.append(
                RiskFactor(
                    category="Injury",
                    severity=RiskLevelEnum.CRITICAL,
                    message=f"Ruled out due to {injury_kind or 'injury'}.",
                    source_type=SourceTypeEnum.FACT,
                )
            )
        elif status == "DOUBTFUL":
            risk_points += 35.0
            factors.append(
                RiskFactor(
                    category="Injury",
                    severity=RiskLevelEnum.HIGH,
                    message=f"Doubtful for next match ({injury_kind or 'injury'}).",
                    source_type=SourceTypeEnum.REPORT,
                )
            )
        else:
            risk_points += 20.0
            factors.append(
                RiskFactor(
                    category="Injury",
                    severity=RiskLevelEnum.MEDIUM,
                    message=f"Managing {injury_kind or 'knock'} (status: {status}).",
                    source_type=SourceTypeEnum.REPORT,
                )
            )

    # 3. Starting probability & minutes
    if starting_prob < 40.0 and not is_injured and not is_suspended:
        risk_points += 30.0
        factors.append(
            RiskFactor(
                category="Playing Time",
                severity=RiskLevelEnum.HIGH,
                message="High likelihood of starting from the bench.",
                source_type=SourceTypeEnum.PREDICTION,
            )
        )
    elif starting_prob < 65.0 and not is_injured and not is_suspended:
        risk_points += 15.0
        factors.append(
            RiskFactor(
                category="Rotation",
                severity=RiskLevelEnum.MEDIUM,
                message="Subject to active squad rotation.",
                source_type=SourceTypeEnum.PREDICTION,
            )
        )

    if minutes_score < 45.0 and not is_injured:
        risk_points += 15.0
        factors.append(
            RiskFactor(
                category="Playing Time",
                severity=RiskLevelEnum.MEDIUM,
                message="Sub-50% minutes over recent fixtures.",
                source_type=SourceTypeEnum.FACT,
            )
        )

    # 4. Form slump
    if form_score < 40.0:
        risk_points += 20.0
        factors.append(
            RiskFactor(
                category="Form",
                severity=RiskLevelEnum.HIGH,
                message=f"Severe form slump (recent form score: {form_score:.1f}).",
                source_type=SourceTypeEnum.FACT,
            )
        )
    elif form_score < 50.0:
        risk_points += 10.0
        factors.append(
            RiskFactor(
                category="Form",
                severity=RiskLevelEnum.LOW,
                message="Below-average scoring in recent matches.",
                source_type=SourceTypeEnum.FACT,
            )
        )

    # 5. Difficult fixtures
    if fixture_score < 35.0:
        risk_points += 15.0
        factors.append(
            RiskFactor(
                category="Schedule",
                severity=RiskLevelEnum.MEDIUM,
                message="Demanding upcoming fixtures against top-tier opponents.",
                source_type=SourceTypeEnum.PREDICTION,
            )
        )

    # 6. Price volatility
    if price_change_7d is not None and price_change_7d <= -15.0:
        risk_points += 15.0
        factors.append(
            RiskFactor(
                category="Market",
                severity=RiskLevelEnum.MEDIUM,
                message=f"Negative price momentum ({price_change_7d:.1f}% over 7 days).",
                source_type=SourceTypeEnum.FACT,
            )
        )

    # Determine overall risk level
    total_risk_score = round(max(0.0, min(100.0, risk_points)), 1)
    if total_risk_score >= 50.0 or is_suspended or (is_injured and (injury_status or "").upper() == "OUT"):
        risk_level = RiskLevelEnum.CRITICAL
    elif total_risk_score >= 35.0:
        risk_level = RiskLevelEnum.HIGH
    elif total_risk_score >= 20.0:
        risk_level = RiskLevelEnum.MEDIUM
    else:
        risk_level = RiskLevelEnum.LOW

    return total_risk_score, risk_level, factors
