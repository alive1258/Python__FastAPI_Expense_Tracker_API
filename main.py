import json
from typing import Annotated, Optional

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field


app = FastAPI()


# =========================
# Pydantic Model
# =========================

class Expense(BaseModel):

    id: Annotated[
        str,
        Field(
            description="The unique ID of the expense",
            examples=["E001"]
        )
    ]

    name: Annotated[
        str,
        Field(
            description="The name of the expense",
            examples=["Grocery Shopping"]
        )
    ]

    amount: Annotated[
        float,
        Field(
            description="The amount of the expense",
            examples=[2500]
        )
    ]

    category: Annotated[
        str,
        Field(
            description="The category of the expense",
            examples=["Food"]
        )
    ]

    date: Annotated[
        str,
        Field(
            description="The date of the expense",
            examples=["2026-09-01"]
        )
    ]

    description: Annotated[
        str,
        Field(
            description="A detailed description of the expense",
            examples=["Monthly groceries and household food items"]
        )
    ]

class ExpenseUpdate(BaseModel):

    id: Annotated[
        Optional[str],
        Field(
            description="The unique ID of the expense",
            examples=["E001"]
        )
    ] = None

    name: Annotated[
        Optional[str],
        Field(
            description="The name of the expense",
            examples=["Grocery Shopping"]
        )
    ] = None

    amount: Annotated[
        Optional[float],
        Field(
            description="The amount of the expense",
            examples=[2500]
        )
    ] = None

    category: Annotated[
        Optional[str],
        Field(
            description="The category of the expense",
            examples=["Food"]
        )
    ] = None

    date: Annotated[
        Optional[str],
        Field(
            description="The date of the expense",
            examples=["2026-09-01"]
        )
    ] = None

    description: Annotated[
        Optional[str],
        Field(
            description="A detailed description of the expense",
            examples=["Monthly groceries and household food items"]
        )
    ] = None

# =========================
# Helper Functions
# =========================

def load_data():
    with open("expenses.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("expenses.json", "w") as f:
        json.dump(data, f, indent=4)


# =========================
# HOME
# =========================

@app.get("/")
async def view():
    return {"Hello": "World"}


# =========================
# READ - Get All Expenses
# =========================

@app.get("/expenses")
async def get_expenses():
    data = load_data()
    return data


# =========================
# READ - Get Specific Expense
# =========================

@app.get("/expenses/{expense_id}")
async def get_specific_expense(
    expense_id: Annotated[
        str,
        Path(
            description="The ID of the expense to retrieve",
            examples=["E001"]
        )
    ]
):
    data = load_data()

    if expense_id in data:
        return data[expense_id]

    raise HTTPException(
        status_code=404,
        detail="Expense not found"
    )


# =========================
# CREATE - Add New Expense
# =========================

@app.post("/expenses", status_code=201)
async def create_expense(expense: Expense):

    data = load_data()

    # Check if ID already exists
    if expense.id in data:
        raise HTTPException(
            status_code=400,
            detail=f"Expense with ID {expense.id} already exists"
        )

    # Add new expense
    data[expense.id] = expense.model_dump(exclude=["id"])

    save_data(data)

    return {
        "message": "Expense created successfully",
        "id": expense.id,
        "expense": data[expense.id]
    }


# =========================
# UPDATE - Update Expense
# =========================

@app.put("/expenses/{expense_id}")
async def update_expense(
    expense_id: Annotated[
        str,
        Path(
            description="The ID of the expense to update",
            examples=["E001"]
        )
    ],
    expense: ExpenseUpdate
):
    data = load_data()

    if expense_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    # Make sure URL ID and body ID match
    if expense.id != expense_id:
        raise HTTPException(
            status_code=400,
            detail="Expense ID in URL and request body must match"
        )

    data[expense_id] = expense.model_dump(exclude_unset=True)

    save_data(data)

    return {
        "message": "Expense updated successfully",
        "id": expense_id,
        "expense": data[expense_id]
    }


# =========================
# DELETE - Delete Expense
# =========================

@app.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: Annotated[
        str,
        Path(
            description="The ID of the expense to delete",
            examples=["E001"]
        )
    ]
):
    data = load_data()

    if expense_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    deleted_expense = data.pop(expense_id)

    save_data(data)

    return {
        "message": "Expense deleted successfully",
        "id": expense_id,
        # "expense": deleted_expense
    }


# =========================
# SORT
# =========================

@app.get("/sort")
async def sort_expenses(
    sort_by: Annotated[
        str,
        "The field to sort by"
    ],
    order: Annotated[
        str,
        "The sorting order"
    ] = "ascending"
):
    data = load_data()

    sorted_data = list(data.values())

    # Validate sort field
    valid_sort_fields = [
        "id",
        "name",
        "amount",
        "category",
        "date",
        "description"
    ]

    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort key: {sort_by}"
        )

    # Validate order
    if order not in ["ascending", "descending"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be 'ascending' or 'descending'"
        )

    # Sort data
    sorted_data.sort(
        key=lambda expense: expense[sort_by],
        reverse=(order == "descending")
    )

    return sorted_data