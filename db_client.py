import abc


class DatabaseClient(abc.ABC):
    @abc.abstractmethod
    def store_file(self, user_id, file, vector_id, filename):
        pass

    @abc.abstractmethod
    def get_files(self, vector_ids):
        pass

    @abc.abstractmethod
    def delete_one(self, vector_id):
        pass

    @abc.abstractmethod
    def close(self):
        pass
