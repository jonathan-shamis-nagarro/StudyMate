from pydantic import BaseModel, ConfigDict, Field

class RetriveDocQueryFields(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    search_text: str = Field(
        title="Text/query to be searched in search index.", example="What is AI Hub?"
    )
    filter: str = Field(
        title="""Filter to be applied on search index.
        
        Equality operators:
            1) eq: Test whether a field is equal to a constant value
                Example: id eq '3'
            2) ne: Test whether a field is not equal to a constant value 
                Example: id ne '3'           
        Range operators:
            1) gt: Test whether a field is greater than a constant value
                Example: id gt 3
            2) lt: Test whether a field is less than a constant value
                Example: id lt 3
            3) ge: Test whether a field is greater than or equal to a constant value
                Example: id ge 3
            4) le: Test whether a field is less than or equal to a constant value
                Example: id le 3
        Logical operators:
            1) and: A binary operator that evaluates to true if both its left and right sub-expressions evaluate to true.
                Example: id gt 3 and id lt 10
            2) or: A binary operator that evaluates to true if either one of its left or right sub-expressions evaluates to true.
                Example: id gt 3 or id eq '10'
            3) not: A unary operator that evaluates to true if its sub-expression evaluates to false, and vice-versa. 
                Example: not id gt 3
        Colection operators:
            1) any: An expression using any returns true if the predicate is true for at least one element of the collection
                Example: Match documents whose tags field contains exactly the string "wifi": tags/any(t: t eq 'wifi')
                         Match documents where the rooms field is empty: not rooms/any()
            2) all: An expression using all returns true if the predicate is true for every element of the collection
                Example: Match documents where every element of the ratings field falls between 3 and 5, inclusive: ratings/all(r: r ge 3 and r le 5)
                         Match documents where (for all rooms) the rooms/amenities field contains "tv", and rooms/baseRate is less than 100: rooms/all(room: room/amenities/any(a: a eq 'tv') and room/baseRate lt 100.0)
        Regular Expressions:
            1) regex: Test whether a field matches a regular expression.
                Example: regex(tag, '/word/')
        Fuzzy Search:
            1) ~: Fuzzy search allows for some typos or misspellings. You can use the ~ operator with a tolerance level
                Example: This will find documents where the tag contains something similar to "word" with a maximum Levenshtein distance of 2 (up to 2 character edits) : tag~'word'~2
        """, example="id" , default=None
    )
    selected_fields: [str] = Field( # type: ignore
        title="indexed fields to be retrived in search query.", example=["id", "title"], default=None
    )
    number_of_documents_retrive: int = Field(
        title="Number of documents to be retrived in search query.", example=10, default=4
    )
    vector_filed_name: str = Field(
        title="vector indexed field for vector query.", example="content", default=None
    )
    