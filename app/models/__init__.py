from app.core.database import Base

#import your models here
from app.models.payment import Transaction
from app.models.rewards import CreditTransaction,AdWatch
from app.models.style import Category,Style,Challenge,Creation,GuestUsage,Collection,CollectionCreation
from app.models.user import User