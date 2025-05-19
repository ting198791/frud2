from client import Client
import taipy.gui.builder as tgb
from state_class import State
from taipy.gui import notify, navigate


def verify_identity(state: State):
    state.open_verification_dialog = not state.open_verification_dialog


def create_id_card_component():
    with tgb.part("id-card"):
        tgb.image(lambda client: client.photo, height="100px", width="100px")

        # Personal Information
        tgb.text(
            lambda client: f" ### {client.first_name} {client.last_name}",
            mode="md",
        )
        tgb.text(lambda client: client.city, class_name="h6")

        tgb.text(
            lambda client: f"{client.job_title}",
            mode="md",
        )

        # Address Section
        with tgb.part("more-info"):
            tgb.text(
                lambda client: f"**Age**: {client.age}",
                mode="md",
            )
            tgb.text(
                lambda client: f"**Address**: {client.street_address}",
                mode="md",
            )
            tgb.text(
                lambda client: f"**City**: {client.city}, **ZIP Code**: {client.zip_code}, **State**: {client.state}",
                mode="md",
            )

        # Action Button
        with tgb.part("text-center"):
            tgb.button(
                "Verify Identity",
                on_action=verify_identity,
                class_name="taipy-button",
            )