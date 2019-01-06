from breeze import breeze
import arrow
import json
import logging
from fuzzywuzzy import process

# Extra endpoints
LIST_ROLES = '/api/volunteers/list_roles'
LIST_VOLUNTEERS = '/api/volunteers/list'
ADD_VOLUNTEER = '/api/volunteers/add'
UPDATE_VOLUNTEER = '/api/volunteers/update'

class MatchNotFoundError(Exception):
    pass


class BreezeProxy():
    def __init__(self, url, api_key):
        self._api = breeze.BreezeApi(url, api_key)
        self._people = []
        self._roles = []

    def get_all_users(self, force=False):
        if force or not self._people:
            self._people = self._api.get_people()

    def get_event_roles(self, event_id):
        return self._api._request(LIST_ROLES, {'instance_id': event_id})

    def get_event_volunteers(self, event_id):
        return self._api._request(LIST_VOLUNTEERS, {'instance_id': event_id})

    def add_event_volunteer(self, event_id, person_id, role_id):
        # First have to add, then can set the role
        payload = {'instance_id': event_id, 'person_id': person_id}
        self._api._request(ADD_VOLUNTEER, payload)
        payload['role_ids_json'] = json.dumps([role_id])
        self._api._request(UPDATE_VOLUNTEER, payload)

    def find_event(self, date):
        return self._api.get_events(f'{date.year}-{date.month}-{date.day}', f'{date.year}-{date.month}-{date.day}')[0]

    def get_breeze_user(self, name):
        self.get_all_users()

        # Put name in format so get_name applies
        temp_name = {'first_name': name, 'last_name': ''}
        get_name = lambda u: ' '.join([u['first_name'], u['last_name']])

        bests = process.extractBests(temp_name, self._people, get_name, limit=3)

        # Penalize 10 points if first names start with different letters
        best = (bests[0], 0) # Hold best candidate and the score
        for item in bests:
            penalty = 0
            if name[0].casefold() != item[0]['first_name'][0].casefold():
                penalty = 10

            if item[1] - penalty > best[1]:
                best = (item, item[1] - penalty)

        if best[1] < 90:
            raise MatchNotFoundError

        return best[0]

    def add_volunteers_to_breeze(self, events_with_assignments):
        items_added = []
        items_not_added = []

        for event in events_with_assignments:
            date = arrow.get(event['date'], 'MMM D, *YYYY')
            event_id = self.find_event(date)['id']
            roles = self.get_event_roles(event_id)
            for assignment in event['assignments']:
                logging.debug(f"Adding {assignment['assignee']} to {assignment['role']}")
                failure_msg = None
                try:
                    assigned_user = self.get_breeze_user(assignment['assignee'])
                    logging.debug(f"Found user: {assigned_user}")
                    assigned_role = process.extractOne({'name': assignment['role']}, roles, lambda x: x['name'])[0]
                    logging.debug(f"Found role: {assigned_role}")
                    self.add_event_volunteer(event_id, assigned_user['id'], assigned_role['id'])
                except breeze.BreezeError:
                    logging.error("BreezeError adding event volunteer")
                    failure_msg = 'Internal error'
                except MatchNotFoundError:
                    logging.error("MatchNotFoundError adding event volunteer")
                    failure_msg = 'Match not found.'

                status_str = "SUCCESS" if not failure_msg else "FAIL"
                logging.info(f"Add {assignment['assignee']} to {assignment['role']} on {date} -- {status_str}")

                data = {'date': event['date'], 'assignee': assignment['assignee'], 'role': assignment['role']}
                if failure_msg:
                    data['error'] = failure_msg
                    items_not_added.append(data)
                else:
                    items_added.append(data)

        return {'itemsAdded': items_added, 'itemsNotAdded': items_not_added}
