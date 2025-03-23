from datetime import UTC, datetime
from uuid import UUID

from models.chat import ChatMessage
from models.task_config.agent import AgentConfig
from models.task_config.base_component import Translations
from models.task_config.chat import ChatConfig
from models.task_config.task_config import (
    ComponentGroup,
    TaskConfig,
    TaskPage,
)

sample_task_config = TaskConfig(
    id="test config",
    name=Translations(languages={"en": "test name", "zh": "测试名字"}, default="en"),
    description=Translations(languages={"en": "test", "zh": "测试描述"}, default="zh"),
    public=True,
    pages=[
        # TaskPage(
        #     label=Translations(languages={"en": "Page title"}),
        #     columns=1,
        #     component_groups=[
        #         ComponentGroup(
        #             label=Translations(languages={"en": "Component group 1"}),
        #             columns=4,
        #             components=[
        #                 Slider(
        #                     id="s1",
        #                     steps=3,
        #                     label=Translations(
        #                         languages={"en": "Slider", "zh": "滑动"}, default="en"
        #                     ),
        #                     labels=[
        #                         Translations(languages={"en": "1"}),
        #                         Translations(languages={"en": "2"}),
        #                         Translations(languages={"en": "3"}),
        #                     ],
        #                 ),
        #                 SingleChoice(
        #                     id="sc1",
        #                     choices=[
        #                         Translations(languages={"en": "1"}),
        #                         Translations(languages={"en": "2"}),
        #                         Translations(languages={"en": "3"}),
        #                     ],
        #                     label=Translations(
        #                         languages={"en": "Single Choice", "zh": "滑动"},
        #                         default="en",
        #                     ),
        #                     shuffle=True,
        #                 ),
        #                 MultiChoice(
        #                     id="mc1",
        #                     choices=[
        #                         Translations(languages={"en": "1"}),
        #                         Translations(languages={"en": "2"}),
        #                         Translations(languages={"en": "3"}),
        #                         Translations(languages={"en": "4"}),
        #                     ],
        #                     label=Translations(
        #                         languages={"en": "Multi Choice", "zh": "滑动"},
        #                         default="en",
        #                     ),
        #                     shuffle=True,
        #                 ),
        #                 FreeText(
        #                     id="f1",
        #                     label=Translations(
        #                         languages={
        #                             "en": "# Free\n~text~ *with* **markdown** [links](https://www.google.com)",
        #                             "zh": "滑动",
        #                         },
        #                         default="en",
        #                     ),
        #                     regex=".*f.*",
        #                 ),
        #             ],
        #         ),
        #     ],
        # ),
        TaskPage(
            label=Translations(languages={"en": "Page title"}),
            columns=2,
            component_groups=[
                ComponentGroup(
                    columns=1,
                    components=[
                        ChatConfig(
                            id="chat",
                            humans_required=1,
                            agents=[
                                AgentConfig(
                                    id="test-agent",
                                    type="TestAgent",
                                )
                            ],
                            order=["human", "test-agent"]
                        )
                    ],
                ),
                # ComponentGroup(
                #     label=Translations(languages={"en": "Component group label"}),
                #     columns=2,
                #     components=[
                #         Slider(
                #             id="s2",
                #             label=Translations(
                #                 languages={"en": "Slider", "zh": "滑动"}, default="en"
                #             ),
                #             steps=3,
                #             labels=[
                #                 Translations(languages={"en": "1"}),
                #                 Translations(languages={"en": "2"}),
                #                 Translations(languages={"en": "3"}),
                #             ],
                #         ),
                #         SingleChoice(
                #             id="sc2",
                #             choices=[
                #                 Translations(languages={"en": "1"}),
                #                 Translations(languages={"en": "2"}),
                #                 Translations(languages={"en": "3"}),
                #             ],
                #             label=Translations(
                #                 languages={"en": "Single Choice", "zh": "滑动"},
                #                 default="en",
                #             ),
                #             shuffle=True,
                #         ),
                #         MultiChoice(
                #             id="mc2",
                #             choices=[
                #                 Translations(languages={"en": "1"}),
                #                 Translations(languages={"en": "2"}),
                #                 Translations(languages={"en": "3"}),
                #             ],
                #             label=Translations(
                #                 languages={"en": "Multi Choice", "zh": "滑动"},
                #                 default="en",
                #             ),
                #             shuffle=True,
                #         ),
                #         FreeText(
                #             id="f2",
                #             label=Translations(
                #                 languages={
                #                     "en": "Free text *with* **markdown** [test](h)",
                #                     "zh": "滑动",
                #                 },
                #                 default="en",
                #             ),
                #             regex=".*f.*",
                #         ),
                #         ChatConfig(
                #             id="chat_component_id",
                #         )
                #     ],
                # ),
            ],
        ),
    ],
)


sample_task_config.model_dump_json()
