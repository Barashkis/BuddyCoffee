from abc import abstractmethod, ABC


class Meeting(ABC):
    @abstractmethod
    def create(self, start_time):
        pass

    @abstractmethod
    def update_date(self, api_id, new_start_time):
        pass
