from pprint import pprint
from sqlite3 import IntegrityError
from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import delete
from sqlmodel import select

from models.database import get_session
from models.task import (
    Task,
    TaskCreate,
    TaskID,
    TaskParticipant,
    TaskParticipantRead,
    TaskRead,
    TaskReadParticipant,
    TaskResponse,
)
from models.task_config.task_config import TaskConfig
from models.user import User, UserID
from settings import SETTINGS

# random.seed(42)

# letters = string.ascii_uppercase
# lang_dict = json.load(open("services/data/lang.json", "r", encoding="utf-8"))


# class Task:
#     def __init__(self):
#         self._id = ""
#         self.title = ""
#         self.desc = ""
#         self.options = {}
#         self.best_choice = "A"
#         self.hidden_incentive = "B"
#         self.scores = {}
#         self.is_complete = False

#     def set_attributes(self, _id, title, desc, options, hidden_incentive, lang):
#         self._id = _id
#         self.title = title
#         self.desc = desc
#         self.options = options
#         # self.permute_options()
#         self.best_choice = self.find_best()
#         self.hidden_incentive = self.find_incentive(hidden_incentive)
#         self.lang = lang
#         self.is_complete = False

#     def permute_options(self):
#         random.shuffle(self.options)

#     def find_best(self):
#         for i, option in enumerate(self.options):
#             if option["option_id"] == "A":
#                 return letters[i]

#     def find_incentive(self, hidden_incentive):
#         for i, option in enumerate(self.options):
#             if option["option_id"] == hidden_incentive:
#                 return letters[i]

#     def parse_options(self):
#         options = []
#         for i, option in enumerate(self.options):
#             option_str = f"{lang_dict['option'][self.lang]} {letters[i]}) {option['desc'][self.lang]}"
#             info_val = option.get("info", "")
#             info_str = []
#             if info_val:
#                 for v in info_val.values():
#                     info_str.append(
#                         f"{v['title'][self.lang]}{lang_dict['is'][self.lang]}{v['value'][self.lang]}"
#                     )
#                 option_str += f" {', '.join(info_str)}."

#             options.append(option_str)
#         return "\n\n".join(options)

#     def parse_scores(self):
#         scores = []
#         for i, (k, v) in enumerate(self.scores.items()):
#             if k != "familiarity" and k != "confidence":
#                 scores.append(f"{letters[i]}: {v}")
#         return ", ".join(scores)

#     def get_changes(self, new_scores):
#         scores = []
#         for k, v in self.scores.items():
#             if v != new_scores[k]:
#                 scores.append(
#                     f"{k if k not in ['confidence', 'familiarity'] else lang_dict[k][self.lang]}: {v} -> {new_scores[k]}"
#                 )
#         if scores:
#             return lang_dict["user_message_change"][self.lang].format(
#                 score_changes=", ".join(scores)
#             )
#         else:
#             return ""

#     def set_scores(self, scores):
#         self.scores = scores

#     def set_complete(self):
#         self.is_complete = True

#     def sort_options(self, list_ids: list):
#         """
#         Sort and update options based on a given mapping.

#         Args:
#             input_mapping (dict): A dictionary mapping current option_ids to original ones (e.g., {'A': 'B', 'B': 'C', 'C': 'D', 'D': 'A'}).
#         """

#         option_letters = ["A", "B", "C", "D"]

#         if not isinstance(self.options, list):
#             raise TypeError(
#                 f"`options` must be a list, but got {type(self.options).__name__}"
#             )

#         for option in self.options:
#             current_id = option["option_id"]
#             option["option_id"] = option_letters[list_ids.index(current_id)]

#         self.options = sorted(self.options, key=lambda x: x["option_id"])

#         self.hidden_incentive = option_letters[list_ids.index(self.hidden_incentive)]
#         self.best_choice = option_letters[list_ids.index(self.best_choice)]


def task_to_task_read(task: Task) -> TaskRead:
    return TaskRead.model_validate(
        task, update={"config": TaskConfig.model_validate(task.config)}
    )


async def create_task(task_create: TaskCreate) -> TaskRead:
    task = Task.model_validate(task_create, update={"login_required": task_create.config.public})
    async with get_session() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task)
    return task_to_task_read(task)


async def delete_task(task_id: UUID4):
    query = delete(Task).where(Task.id == task_id)
    async with get_session() as session:
        await session.execute(query)
        await session.commit()


async def get_participant_tasks(user_id: UserID) -> list[TaskReadParticipant]:

    query = (
        select(Task, TaskResponse)
        .outerjoin(
            TaskParticipant,
            Task.id == TaskParticipant.task,  # type: ignore
        )
        .outerjoin(
            TaskResponse,
            (TaskResponse.user == TaskParticipant.user),  # type: ignore
        )
        .where(TaskParticipant.user == user_id | Task.public)
    )
    async with get_session() as session:
        results: list[tuple[Task, TaskResponse]] = list(
            (await session.execute(query)).all()
        )

    return [
        TaskReadParticipant(
            config=TaskConfig.model_validate(task.config),
            id=task.id,
            public=TaskConfig.model_validate(task.config).public,
            completed=bool(response),
        )
        for task, response in results
    ]


# async def get_user_tasks(user_id: UserID) -> UserTasksWithResponses:
#     query = select(Task, User, TaskParticipant).outerjoin(
#         TaskParticipant,
#         (Task.id == TaskParticipant.task) & (TaskParticipant.user == user_id),  # type: ignore
#     )
#     async with get_session() as session:
#         results: list[tuple[Task, User, TaskParticipant]] = list(
#             (await session.execute(query)).all()
#         )

#     my_tasks = MyTasks(created=[], participating=[])
#     for task, user, task_participant in results:
#         task_read = TaskRead.model_validate(task, update={"creator": user})

#         if task_participant:
#             my_tasks.participating.append(task_read)
#     return my_tasks


async def get_participant_task(
    task_id: TaskID, user_id: UserID
) -> tuple[TaskReadParticipant | None, bool]:
    """
    A user is authorized to to access a task if they are one of the task's participants
    Returns 2-tuple:
    1. `Task`: the task exists
       `None`: the task does not exist
    2. `True`: the user is authorized
       `False`: the doesn't exist or the user is unauthorized
    """

    query = (
        select(
            Task,
            TaskParticipant.user,
            TaskResponse,
        )
        .outerjoin(
            TaskParticipant,
            (Task.id == TaskParticipant.task) & (TaskParticipant.user == user_id),  # type: ignore
        )
        .outerjoin(TaskResponse, (Task.id == task_id) & (TaskResponse.user == user_id))
        .where(Task.id == task_id)
    )

    async with get_session() as session:
        result: tuple[Task | None, UserID | None, TaskResponse | None] = (
            await session.execute(query)
        ).first()

    if not result:
        return None, True
    task, is_participant, completed = result
    if not task:
        return None, True
    task.config = TaskConfig.model_validate(task.config)
    if not task.config.public:
        return TaskReadParticipant(**task.model_dump(), completed=False), True
    return TaskReadParticipant(**task.model_dump(), completed=bool(completed)), bool(
        is_participant
    )


async def get_task_participants(task_id: UUID4) -> list[TaskParticipantRead]:
    query = (
        select(TaskParticipant, TaskResponse)
        .outerjoin(
            TaskResponse,
            (TaskParticipant.task == task_id) & (TaskResponse.task == task_id),
        )
        .where(TaskParticipant.task == task_id)
    )
    async with get_session() as session:
        results: list[tuple[TaskParticipant, TaskResponse]] = (
            await session.execute(query)
        ).all()
    return [
        TaskParticipantRead(task=tp.task, user=tp.user, completed=bool(tr))
        for tp, tr in results
    ]

async def create_participant(task_id: UUID4, participant_id: UUID4 | None) -> TaskParticipantRead | None:
    if not await Task.get(task_id):
        return None
    
    if not participant_id:
        participant_id = uuid4()
    user = await User.get(participant_id)
    if not user:
        user = await User(id=participant_id).save()
    try:
        await TaskParticipant(task=task_id, user=user.id).save()
    except IntegrityError:
        ...
    return TaskParticipantRead(task=task_id, user=participant_id, completed=False)