from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project):

        # insert_one is from motor, as project is pydantic object , and insert one takes only dictinalry
        result = await self.collection.insert_one(
            project.dict(by_alias=True, exclude_unset=True)
        )  # no we will use alias (_id while pydantic see it as _id)

        # _id (it will be created once we inseted in the data)
        project.id = result.inserted_id

        return project

    async def get_or_create_one(
        self, project_id: str
    ):  # we get the project if its already there and if its not we create it.
        record = await self.collection.find_one(
            {"project_id": project_id}  # -> the filter <-
        )  # find_one is from motor

        if record is None:  # the project is not found, so we will need to create it
            # create project
            project = Project(project_id=project_id)  # Project -> our data model
            project = await self.create_project(project=project)

            return project

        # return record  # this will not work as record is a dictinary, as find_one return a dictiionary , and insert_one take a dictionary
        # its like i give evry model in the dictionary to the model , so the output will be project model
        return Project(**record)

    # 1,10 are default values
    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        # count total number of documents (records)
        # count_documents is from motor, {} is an empty filter
        total_documents = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        # collecting data form the db
        # we use this way insead of loading the whole data (network and memory problems will happen if i load the whole data in the DB)
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = []
        async for document in cursor:  # as cursor is from collection.find -> motor and this is async so we add async to the for loop
            projects.append(Project(**document))

        return projects, total_pages
