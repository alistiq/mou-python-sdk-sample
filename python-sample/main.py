import asyncio
from os import getenv
from mou_repository import MouRepository

async def main():
    async with MouRepository(lang="sk") as repo:
        if await repo.has_service_dataset_access():
            print(f"Already have dataset access for user {getenv('MOU_USER_NAME')}")
        else:
            print("Don't have dataset access, should ask for one")
            await repo.request_service_dataset_access()

            # after the request has been sent, we can either let user tell us it's done (via UI)
            # or check periodically, that the grant was given
            access = await repo.await_dataset_access()

            if not access:
                print("The user did not grant access to datasets, we cannot continue!")
                return

        # only an example of how to work with datasets, the consumer needs to implement
        # his usecases..
        data = await repo.extract_personal_data_for_residency()
        print(f"Output data: {data}")


asyncio.run(main())
