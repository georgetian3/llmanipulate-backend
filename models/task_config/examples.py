from datetime import UTC, datetime
from uuid import UUID, uuid4

from models.models import ChatHistory, ChatMessage
from models.task_config.base_component import Translations
from models.task_config.chat import Chat
from models.task_config.task_config import (
    ComponentGroup,
    FreeText,
    MultiChoice,
    SingleChoice,
    Slider,
    TaskConfig,
    TaskPage,
)

sample_task_config = TaskConfig(
    id="test config",
    name=Translations(languages={"en": "test name", "zh": "测试名字"}, default="en"),
    description=Translations(languages={"en": "test", "zh": "测试描述"}, default="zh"),
    pages=[
        TaskPage(
            label=Translations(languages={"en": "Page title"}),
            columns=1,
            component_groups=[
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 1"}),
                    columns=4,
                    components=[
                        Slider(
                            id="s1",
                            steps=3,
                            label=Translations(
                                languages={"en": "Slider", "zh": "滑动"}, default="en"
                            ),
                            labels=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                        ),
                        SingleChoice(
                            id="sc1",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                            label=Translations(
                                languages={"en": "Single Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc1",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                                Translations(languages={"en": "4"}),
                            ],
                            label=Translations(
                                languages={"en": "Multi Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f1",
                            label=Translations(
                                languages={
                                    "en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)",
                                    "zh": "滑动",
                                },
                                default="en",
                            ),
                            regex=".*f.*",
                        ),
                    ],
                ),
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 2"}),
                    columns=2,
                    components=[
                        Slider(
                            id="s12",
                            steps=3,
                            label=Translations(
                                languages={"en": "Slider", "zh": "滑动"}, default="en"
                            ),
                            labels=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                        ),
                        SingleChoice(
                            id="sc12",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                            label=Translations(
                                languages={"en": "Single Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc12",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                                Translations(languages={"en": "4"}),
                            ],
                            label=Translations(
                                languages={"en": "Multi Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f12",
                            label=Translations(
                                languages={
                                    "en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)",
                                    "zh": "滑动",
                                },
                                default="en",
                            ),
                            regex=".*f.*",
                        ),
                    ],
                ),
                ComponentGroup(
                    label=Translations(languages={"en": "Component group 3"}),
                    columns=1,
                    components=[
                        Slider(
                            id="s13",
                            steps=3,
                            label=Translations(
                                languages={"en": "Slider", "zh": "滑动"}, default="en"
                            ),
                            labels=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                        ),
                        SingleChoice(
                            id="sc13",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                            label=Translations(
                                languages={"en": "Single Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc13",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                                Translations(languages={"en": "4"}),
                            ],
                            label=Translations(
                                languages={"en": "Multi Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f13",
                            label=Translations(
                                languages={
                                    "en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)",
                                    "zh": "滑动",
                                },
                                default="en",
                            ),
                            regex=".*f.*",
                        ),
                    ],
                ),
            ],
        ),
        TaskPage(
            label=Translations(languages={"en": "Page title"}),
            columns=2,
            component_groups=[
                ComponentGroup(columns=1, components=[Chat(id="chat")]),
                ComponentGroup(
                    label=Translations(languages={"en": "Component group label"}),
                    columns=2,
                    components=[
                        Slider(
                            id="s2",
                            label=Translations(
                                languages={"en": "Slider", "zh": "滑动"}, default="en"
                            ),
                            steps=3,
                            labels=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                        ),
                        SingleChoice(
                            id="sc2",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                            label=Translations(
                                languages={"en": "Single Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        MultiChoice(
                            id="mc2",
                            choices=[
                                Translations(languages={"en": "1"}),
                                Translations(languages={"en": "2"}),
                                Translations(languages={"en": "3"}),
                            ],
                            label=Translations(
                                languages={"en": "Multi Choice", "zh": "滑动"},
                                default="en",
                            ),
                            shuffle=True,
                        ),
                        FreeText(
                            id="f2",
                            label=Translations(
                                languages={
                                    "en": "Free text *with* **markdown** [test](h)",
                                    "zh": "滑动",
                                },
                                default="en",
                            ),
                            regex=".*f.*",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


sample_chat_history = ChatHistory(
    id="sample chat history",
    messages=[
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 2, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 3, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 4, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test ",
            timestamp=datetime(2025, 1, 1, 1, 1, 4, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 5, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 6, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="1aafee69bd724e7cb7c04898581aaf59", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 7, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 8, tzinfo=UTC),
        ),
        ChatMessage(
            sender=UUID(hex="255f1f3227924947980d44328dd8c174", version=4),
            message="test",
            timestamp=datetime(2025, 1, 1, 1, 1, 9, tzinfo=UTC),
        ),
    ],
)
