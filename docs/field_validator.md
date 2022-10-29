# Field validator

Custom validation is not an easy task in this case. But we still can achieve it by using threads.

Because we define a validator to validate fields on inheriting models, we should set `check_fields=False` on the validator. More information can be found [here](https://pydantic-docs.helpmanual.io/usage/validators/).

```python
# schemas.py

import asyncio
import concurrent.futures

from asgiref.sync import sync_to_async
from dantico import ModelSchema
from pydantic import validator

from users.models import User


class UserSchema(ModelSchema):
    class Config:
        model = User
        exclude = ["password"]

    @validator("username", check_fields=False)
    def validate_username(cls, v):
        """
        Here we are using async method as validator. Because there is
        already an event loop (using FastAPI), we need to start another thread.

        :param cls: Access the class of the object that is being validated
        :param v: Validate the value
        :return: The result of the username_must_be_unique function
        """

        @sync_to_async
        def username_must_be_unique():
            if User.objects.filter(username__icontains=v).exists():
                raise ValueError("username already exists")
            return v

        # A way to run async code in a sync environment.
        pool = concurrent.futures.ThreadPoolExecutor(1)
        result = pool.submit(asyncio.run, username_must_be_unique()).result()

        return result
```
