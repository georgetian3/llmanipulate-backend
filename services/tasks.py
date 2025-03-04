from pprint import pprint
from sqlmodel import select

from models.database import get_session
from models.task import MyTasks, Task, TaskID, TaskParticipant, TaskRead, TaskResponse
from models.user import User, UserID

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


async def get_user_tasks(user_id: UserID) -> MyTasks:
    query = (
        select(Task, User, TaskParticipant)
        .join(User, Task.creator == User.id)
        .join(
            TaskParticipant,
            ((Task.id == TaskParticipant.task) & (TaskParticipant.user == user_id)),
            isouter=True,
        )
    )
    async with get_session() as session:
        results: list[tuple[Task, User, TaskParticipant]] = list(
            (await session.execute(query)).all()
        )

    my_tasks = MyTasks(created=[], participating=[])
    for task, user, task_participant in results:
        task_read = TaskRead.model_validate(task, update={"creator": user})
        if task.creator == user_id:
            my_tasks.created.append(task_read)
        if task_participant:
            my_tasks.participating.append(task_read)
    return my_tasks


async def get_task(
    task_id: TaskID, user_id: UserID
) -> tuple[TaskRead | None, bool | None]:
    """
    A user is authorized to to access a task if they satisfy at least one of the following requirements:
    1. the user is the task's creator
    2. the user is the task's participant
    3. the task is public
    Returns 2-tuple:
    1. `Task`: the task exists
       `None`: the task does not exist
    2. `True`: the task exists and the user is authorized
       `False`: the task exists and the user is unauthorized
       `None`: the task does not exist
    """
    query = (
        select(
            Task,
            User,
            TaskParticipant.user,
        )
        .join(User, Task.creator == User.id)
        .outerjoin(
            TaskParticipant,
            (Task.id == TaskParticipant.task) & (TaskParticipant.user == user_id),
        )
        .where(Task.id == task_id)
    )

    async with get_session() as session:
        result: tuple[Task | None, User | None, UserID | None] = (
            await session.execute(query)
        ).first()

    task, creator, is_participant = result if result else (None, None, None)
    if not result:
        return None, None
    return TaskRead.model_validate(task, update={"creator": creator}), (
        task.public or task.creator == user_id or is_participant is not None
    )


async def get_task_response(task_id: TaskID, user_id: UserID) -> TaskResponse | None:
    async with get_session() as session:
        return (
            await session.execute(
                select(TaskResponse).where(
                    TaskResponse.task == task_id, TaskResponse.user == user_id
                )
            )
        ).scalar_one_or_none()
