from uuid import uuid4

from pydantic import UUID4
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import select

from models.database import get_session
from models.models import to_model
from models.task import (
    Task,
    TaskCreate,
    TaskRead,
    TaskReadParticipant,
)
from models.task_config.task_config import TaskConfig
from models.task_participant import TaskParticipant, TaskParticipantRead
from models.task_response import TaskResponse
from models.user import User
from services.logging import get_logger

logger = get_logger(__name__)

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


async def create_task(task_create: TaskCreate) -> TaskRead:
    task = Task(
        id=uuid4(), **task_create.model_dump(), public=task_create.config.public
    )
    async with get_session() as session:
        session.add(task)
        await session.commit()
        await session.refresh(task)
        # add agents to separate table
        # session.add_all(
        #     [
        #         Agent(
        #             **agent.model_dump(),
        #             task=task.id,
        #             component=component.id,
        #         )
        #         for component in task_create.config.components
        #         if component.type == "chat"
        #         for agent in component.agents
        #     ]
        # )
        # await session.commit()
        # await session.refresh(task)
    return to_model(task, TaskRead)


async def delete_task(task_id: UUID4):
    query = delete(Task).where(Task.id == task_id)  # type: ignore
    async with get_session() as session:
        await session.execute(query)
        await session.commit()


async def get_task(
    task_id: UUID4, user_id: UUID4
) -> tuple[TaskReadParticipant | None, bool]:
    """
    A user is authorized to to access a task if they are one of the task's participants
    Returns 2-tuple:
    1. `Task`: the task exists
       `None`: the task does not exist
    2. `True`: the user is authorized
       `False`: the doesn't exist or the user is unauthorized
    """
    logger.debug(f"Getting task {task_id} for user {user_id}")
    query = (
        select(
            Task,
            TaskParticipant.user_id,
            TaskResponse,
        )
        .outerjoin(
            TaskParticipant,
            (Task.id == TaskParticipant.task_id) & (TaskParticipant.user_id == user_id),  # type: ignore
        )
        .outerjoin(
            TaskResponse, (Task.id == task_id) & (TaskResponse.user_id == user_id)
        )  # type: ignore
        .where(Task.id == task_id)
    )

    async with get_session() as session:
        result: tuple[Task, UUID4 | None, TaskResponse | None] = (
            await session.execute(query)
        ).first()

        if not result:
            logger.debug(f"Task {task_id} not found")
            return None, True
        task, is_participant, completed = result
        task.config = TaskConfig.model_validate(task.config)
        if task.config.public and not is_participant:
            await session.execute(
                pg_insert(User)
                .values(**User(id=user_id, autogenerated=True).model_dump())
                .on_conflict_do_nothing()
            )
            session.add(TaskParticipant(task_id=task_id, user_id=user_id))
            await session.commit()
            is_participant = True
        await session.refresh(task)
        return TaskReadParticipant(
            id=task.id, config=task.config, completed=bool(completed)
        ), bool(is_participant)


async def get_task_participants(task_id: UUID4) -> list[TaskParticipantRead]:
    query = (
        select(TaskParticipant, TaskResponse)
        .outerjoin(
            TaskResponse,
            (TaskParticipant.task_id == task_id) & (TaskResponse.task == task_id),  # type: ignore
        )
        .where(TaskParticipant.task_id == task_id)
    )
    async with get_session() as session:
        results: list[tuple[TaskParticipant, TaskResponse]] = (
            await session.execute(query)
        ).all()
    return [
        TaskParticipantRead(task_id=tp.task_id, user_id=tp.user_id, completed=bool(tr))
        for tp, tr in results
    ]
