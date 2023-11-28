import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK

from app.models.cleaning import CleaningInDB


class TestCleaningsRoutes:
    @pytest.mark.anyio
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    @pytest.mark.anyio
    async def test_invalid_input_raises_error(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code != HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCleaning:
    async def test_get_cleaning_by_id(
            self,
            app: FastAPI,
            client: AsyncClient,
            test_cleaning: CleaningInDB,
    ) -> None:
        res = await client.get(
            app.url_path_for(
                "cleanings:get-cleaning-by-id",
                id=test_cleaning.id,
            ),
        )
        assert res.status_code == HTTP_200_OK
        cleaning = CleaningInDB(**res.json())
        assert cleaning == test_cleaning

    @pytest.mark.parametrize(
        "id, status_code",
        (
                (500, 404),
                (-1, 404),
                (None, 422),
        ),
    )
    async def test_wrong_id_returns_error(
            self, app: FastAPI, client: AsyncClient, id: int, status_code: int
    ) -> None:
        res = await client.get(
            app.url_path_for("cleanings:get-cleaning-by-id", id=id),
        )
        assert res.status_code == status_code

    async def test_get_all_cleanings_returns_valid_response(
            self, app: FastAPI, client: AsyncClient, test_cleaning: CleaningInDB
    ) -> None:
        res = await client.get(app.url_path_for("cleanings:get-all-cleanings"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        cleanings = [CleaningInDB(**l) for l in res.json()]
        assert test_cleaning in cleanings
