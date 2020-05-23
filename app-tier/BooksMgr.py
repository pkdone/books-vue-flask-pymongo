from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.son import SON
from pprint import pprint


##
# Class for managing access to a MongoDB 'books' collection
##
class BooksMgr:

    ##
    # Initialise MongoDB connection, database and collection handles
    ##
    def __init__(self, uri, dbname, collname):
        self.uri = uri
        self.connection = MongoClient(host=uri)
        self.db = self.connection[dbname]
        self.coll = self.db[collname]

    ##
    # Return the list of all books (or a subset if a limit is specified) in an order
    ##
    def list(self, skip=0, limit=0, sortdesc=None, sortasc=None):
        # print(locals());

        if skip is None:
            skip = 0

        if limit is None:
            limit = 0

        if sortdesc:
            sort = [(sortdesc, DESCENDING)]
        elif sortasc:
            sort = [(sortasc, ASCENDING)]
        else:
            sort = None

        cursor = self.coll.find({}, {'_id': 0, 'id': 1, 'title': 1, 'author': 1, 'read': 1,
                                'score': 1}, skip=int(skip), limit=int(limit), sort=sort)
        return [book for book in cursor]

    ##
    # Insert a new book document into the collection
    ##
    def create(self, new_book):
        self.validate_and_default_fields(new_book)
        result = self.coll.insert_one(new_book)
        return True if result.inserted_id else False

    ##
    # Query a specific book's details by its id
    ##
    def read(self, id):
        if not id:
            raise ValueError('No book id specified')

        return self.coll.find_one({'id': id}, {'_id': 0, 'id': 1, 'title': 1, 'author': 1,
                                  'read': 1, 'score': 1})

    ##
    # Update a specific book, by id, with new field values
    ##
    def update(self, id, book_to_update):
        if 'id' not in book_to_update:
            book_to_update['id'] = id

        self.validate_and_default_fields(book_to_update)
        pprint(book_to_update)
        result = self.coll.update_one({'id': id}, {'$set': book_to_update})
        return True if result.modified_count else False

    ##
    # Remove a specific book by its id
    ##
    def delete(self, id):
        if not id:
            raise ValueError('No book id specified')

        result = self.coll.delete_one({'id': id})
        return True if result.deleted_count else False

    ##
    # For specific book data, ensure minimum required fields are specified
    ##
    def validate_and_default_fields(self, book):
        if not book:
            raise ValueError('No book data provided')

        if 'id' not in book:
            raise ValueError('No book "id" field specified')

        if 'title' not in book:
            raise ValueError('No book "title" field specified')

        if 'author' not in book:
            raise ValueError('No book "author" field specified')

        if 'read' not in book:
            book['read'] = False
