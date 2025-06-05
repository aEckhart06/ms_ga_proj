// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use('ms_ga_contestants');

// Create a new document in the collection.
db.getCollection('contestants').insertOne({
    "name": "Samantha de Haan"
});
