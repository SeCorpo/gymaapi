from database import get_db
from model.Person import Person
from model.Gyma import Gyma
import datetime


def start_gyma(person_id):
    if person_id is None:
        raise Exception("Gyma requires a person_id")

    new_gyma = Gyma(
        person_id=person_id,
        time_of_arrival=datetime.datetime.now()
    )
    # add gyma id to the session, so exercises can be easily add
#     return True if added in database


def end_gyma(person_id, gyma_id):
    if person_id is None:
        raise Exception("Gyma requires a person_id")

    if gyma_id is None:
        raise Exception("Gyma cannot be altered without a gyma_id")

    # gyma = get gyma from database with person_id and gyma_id
    # gyma.set_time_of_arrival(datetime.datetime.now())
