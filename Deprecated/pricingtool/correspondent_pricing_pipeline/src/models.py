from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Boolean

class Base(DeclarativeBase):
    pass

class State(Base):
    __tablename__ = "states"
    StateFULL: Mapped[str] = mapped_column(String, primary_key=True)
    StateAbreviation: Mapped[str] = mapped_column(String, nullable=True)
    NJD_JD: Mapped[str] = mapped_column(String, nullable=True)
    AHL_AvailableStates: Mapped[bool] = mapped_column(Boolean, nullable=True)
    AHL_LicenseRequiredBusinessPurposeStates: Mapped[bool] = mapped_column(Boolean, nullable=True)

class PricingMatrix(Base):
    __tablename__ = "pricing_matrix"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Experience_Level: Mapped[str] = mapped_column(String)
    Project_Type: Mapped[str] = mapped_column(String)
    Loan_Type: Mapped[str] = mapped_column(String)
    FICO: Mapped[str] = mapped_column(String)
    Number_of_Units: Mapped[str] = mapped_column(String)

    Max_LTAIV: Mapped[float] = mapped_column(Float, nullable=True)
    Max_LTC: Mapped[float] = mapped_column(Float, nullable=True)
    Max_LTARV: Mapped[float] = mapped_column(Float, nullable=True)
    Base_Rate: Mapped[float] = mapped_column(Float, nullable=True)
    Loan_Level_Adj: Mapped[float] = mapped_column(Float, nullable=True)
    Adj_Rate: Mapped[float] = mapped_column(Float, nullable=True)
    Min_Loan_Amount: Mapped[float] = mapped_column(Float, nullable=True)
    Max_Loan_Amount: Mapped[float] = mapped_column(Float, nullable=True)
    Max_Cash_Out: Mapped[float] = mapped_column(Float, nullable=True)

class Deal(Base):
    __tablename__ = "deals"
    # Minimal subset used for pricing — add more columns as needed
    Record_ID: Mapped[str] = mapped_column(String, primary_key=True)
    Property_State: Mapped[str] = mapped_column(String, nullable=True)
    Fico: Mapped[float] = mapped_column(Float, nullable=True)
    Borrower_Experience_Number_of_Projects: Mapped[float] = mapped_column(Float, nullable=True)
    Number_of_Units: Mapped[int] = mapped_column(Integer, nullable=True)
    Product_Type: Mapped[str] = mapped_column(String, nullable=True)
    SM_Loan_Type: Mapped[str] = mapped_column(String, nullable=True)
    Improvement_Budget: Mapped[float] = mapped_column(Float, nullable=True)
    ARV: Mapped[float] = mapped_column(Float, nullable=True)
    Purchase_Price: Mapped[float] = mapped_column(Float, nullable=True)
    Requested_Loan_Amount: Mapped[float] = mapped_column(Float, nullable=True)

    # Derived
    experience_bucket: Mapped[str] = mapped_column(String, nullable=True)
    fico_bucket: Mapped[str] = mapped_column(String, nullable=True)
    units_bucket: Mapped[str] = mapped_column(String, nullable=True)
    loan_type_norm: Mapped[str] = mapped_column(String, nullable=True)
    project_type_norm: Mapped[str] = mapped_column(String, nullable=True)
