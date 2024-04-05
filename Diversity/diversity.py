from idp_engine import IDP, Theory
from idp_engine.Parse import TheoryBlock, Structure
from idp_engine.Run import model_expand
from typing import Union, Iterator

class idp(IDP):

    # -> is a function annotation to document the return value for a function
    # code:str means that code is expected to be a string
    # cls means that the method is a class method
    # Union defines that the variable van hold values of different types
    def from_str(cls, code:str) -> "IDP":
        IDP.from_str(cls, code)

    # Iterator is an object
    def model_expand(*theories: Union[TheoryBlock, Structure, Theory],
                 max: int = 10,
                 timeout_seconds: int = 10,
                 complete: bool = False,
                 extended: bool = False,
                 sort: bool = False
                 ) -> Iterator[str]:
        model_expand(theories,max,timeout_seconds,complete,extended,sort)
    
    
    def diverse_model_generation(n:int,k:int,relevant:str,method:str):
        return

