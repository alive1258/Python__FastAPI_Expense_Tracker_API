import json
from fastapi import FastAPI, HTTPException, Path

app = FastAPI()


def load_data():
    with open("expenses.json", "r") as f:
        data = json.load(f)

    return data


@app.get("/")
async def view():
    return {"Hello": "World"}


@app.get("/expenses")
async def get_expenses():
    data = load_data()
    return data


@app.get("/expenses/{expense_id}")
async def get_specific_expense(
    expense_id: str = Path(
        ...,
        description="The ID of the expense to retrieve",
        example="E001"
    )
):
    data = load_data()

    if expense_id in data:
        return data[expense_id]

    raise HTTPException(
        status_code=404,
        detail="Expense not found"
    )


@app.get("/sort")
async def sort_expenses(
    sort_by: str,
    order: str = "ascending"
):
    data = load_data()

    sorted_data = list(data.values())

    def get_sort_key(expense):
        if sort_by in expense:
            return expense[sort_by]

        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort key: {sort_by}"
        )

    if order not in ["ascending", "descending"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be 'ascending' or 'descending'"
        )

    sorted_data.sort(
        key=get_sort_key,
        reverse=(order == "descending")
    )

    return sorted_data