from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "diet_surveys" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "surveyed_date" DATE NOT NULL,
    "soup_stew_per_day" INT NOT NULL,
    "sweet_drink_per_day" INT NOT NULL,
    "fried_food_per_week" INT NOT NULL,
    "vegetables_every_meal" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "diet_surveys"."surveyed_date" IS '설문 응답일';
COMMENT ON COLUMN "diet_surveys"."soup_stew_per_day" IS '하루 국/찌개 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."sweet_drink_per_day" IS '하루 단 음료 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."fried_food_per_week" IS '주당 튀김/볶음 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."vegetables_every_meal" IS '매 식사 채소 섭취 여부';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "diet_surveys";"""


MODELS_STATE = (
    "eJztXW2TorgW/iuUn+ZW3Z0B1Fa7aj74wnS7Y3fP2s7eubtuUSFEpURwAafH2jv7229OAB"
    "UIDtp2gy5fWgg5QJ4cTs55cpL+q7KwdWK6b9vEMfCsci38VbHQgtCD2JV/CxW0XG7LocBD"
    "msmqom0dzfUchD1aOkGmS2iRTlzsGEvPsC1aaq1MEwptTCsa1nRbtLKMP1dE9ewp8WbEoR"
    "d+/4MWG5ZOvhE3PF3O1YlBTD3yqoYOz2blqrdesrK+5X1gFeFpmoptc7WwtpWXa29mW5va"
    "huVB6ZRYxEEegdt7zgpeH94uaGfYIv9Nt1X8V9yR0ckErUxvp7kZMcC2BfjRt3FZA6fwlJ"
    "9kqdaoNatXtSatwt5kU9L47jdv23ZfkCFwP6p8Z9eRh/waDMYtbl+J48IrJcDrzpDDR29H"
    "JAYhffE4hCFg+zAMC7YgbhXnRCgu0DfVJNbUAwWX6/U9mP3aHnZv28M3tNa/oDU2VWZfx+"
    "+DS7J/DYDdAgmfxgEgBtXPE0BJFDMASGulAsiuRQGkT/SI/w1GQfz58eGeD+KOSAxI3cCe"
    "8D/BNNzER10MQPfgB+2Fl1647p/mLmxv7tpf4oh2Bw8d1n7b9aYOuwu7QYeiC8ZyMt/57K"
    "FAQ3j+hBxdTVyxZTutbvLSQl7ES5CFpgwraDG0Lxg+PrvMlCeGFVa+d1BZ0RpuscaUjjG9"
    "oGGlJcvVakMWq1fNeq3RqDfFzfiSvLRvoOn0b2CsiejmjwcfskCGeYjV3Aicp92sZTGbtX"
    "SrWUsYzRlyZ0RXl8h1n2yHo6/pWHJEzxNVSW5mGY3kZvpoBNeiwLLfA9AM658nhHIWxZTT"
    "FVNOKCZtse6b9ySCirVaMBT79JWQhUkCza10znhW7toD5VqAv2Prg+Kf+b+VI3C+ygDzVS"
    "rKV3GQNcPxZjpaJ2HuUXD4irorE3eaqJBnLMhbOCim2u7Br9ceKTF8lrR1RKXapqWpIh+j"
    "uNx5ftSSlMUsSulWUYrrm+Gq1AkzvnIsY8e2TYKsFMdoVy4GpkYFXwrNjdN0al3rPDwMIi"
    "56px9zfu4/33UUCi9Dl1YyvIhPFMVUXxicCPyHkIZir4jood53LpCayPVU057yQO0FNo6P"
    "alRyn3mEgwwgBxpYDAs56t8pj6P23acIzmA34YrMStex0sRwtLmJ8J/+6FaAU+G3h3slHo"
    "Ru6o1+q8A7oZVnq5b9RNV2t9lhcVgUpQQcAtCqiMMK7O/IqOQJOjIPa07boD9Y5jrQozPp"
    "2UDl93bsaqkf2bFRybJjc+1Y9vIHsEw7cStBpjdT8YzgucsZ+gLxDx+HxEQen20OaKRbdq"
    "su3KmY3f091OGwdNvtO2OWMSGutzaJ6q6cr2T9TFAG4e0e2d3OGBjgAKmeIBP8WvJMWIBy"
    "7Ib3OmNQLNszJgZmrX0mJPc7tzozRF6StN61KhzuOmZ00inshKErqeyLpLJZB1O/JKROst"
    "IxcbnCUDKV8Qrhpjhe4Rau0b+NBs7GeB1G0bhr17NNA6saZ/o0VT1jUj/W05eGCstSk/7V"
    "W3UKG6lS2PQrEUrq9XpGovAkE/1bYHUDHYNsXKwA0DYaoH9XtVpRoJ1QiOjz1Km5wrbL+d"
    "w/mDZKwZcjG4N4AsKv/6lPqOZq7K8PryZPWsJi+k4fPP+zf/jcGSjCp6HS7T/2g8ntTdTC"
    "LkYpnaHSHsSzAyCgNyzDOgzuqNiRSJ+MxKlsdBcjXaAn4hWmSDd9dQYF1+WJCNhjXCDsPd"
    "tDJnVhbJPGFMSxOVO2e7qAK12AnsC6BH1AVX7bBzKCPpBqrOSqVqA+mOnH9wBHNnf8b3uD"
    "8wGfPnxqrjFxDJ0Xge5T/rhk7sCDQydJ9K9UlZhzB/YGy0Wy9U/EmM44zOAenLciRRhNMd"
    "ZqPs7CfFoISGeHQzorFqQygVikgeoCXhQCUm1hHIRnUL8QYAb6icHPa+BWaAcgihHegG2Q"
    "wAgT8Eh8s4zruuiXg9VutMBoVPWWAJ4jCw9Fzc8Oyb1bnpDheio2HLxaTIhDgvSS7JaEL1"
    "8Au63XWX+1EPRNrd70B86ifA5kOnFU6mEYC4bGIZAnRQuANo3lQa+bUl0gNx+GwmLwbmFY"
    "76S3jepivBJFTS4E7Hiuq47hzlUX286BsVFCNHfY78Ap1BAC3a42mkL3Y4/ZGxE8w7rOin"
    "FNEN+Kf0tvxcJ0gOuhaUq24I9z3SI3OCrT6HT430jXwo00tm5k+ivT32qbHlTbcNSBow49"
    "qtGDGv2t09+sDEwkMamaIS+pmpqWVOWsvFCnjr1KWX/x4x6I3CDnHoh/AeCcA+fFDBEdbf"
    "UJs/uTlvBmqPzy093gJ1GsZhx5YzmfWVI+0zM+E8s3ylyNS5jSL3M1LrRj+RPrh84L7gjl"
    "PDNQwPnBRCZMFGyOc0b9LmNqfSTrxACVnr9QTJTTJulpsYOeNjPSuwpEm0cbRXzPqtt+7L"
    "Z7SuV7PmvU4vkynCl/TkpN+rQ/N52nnPq/yKl/v4ePmPtPCBZp8h9LMg26NK3aZBFYXWJT"
    "gvUXzARY2HOYGaU20FtxWPZsvnzyLnmvIKKRa+MKqPb6RAQoRSzBzJ+eEcSo075Pe0OnvZ"
    "HqtDfiTrtOH83gmjiEttPCnKVE2XDn3yl/7HED5pNwcwLEpUZqAYVwDPZSlohJSg+ZpETM"
    "RFvjYMMl1ACsXXVJR8YnQubJLki11ek3KEDeBsU8SCOA9A1gnAPKGCxISDaLfzeyRq8nzu"
    "JwTUKW6sxeOT5y3HV0e+izFPncOTRgynxymIDp1qvA7yOdMOPD0pQ01KixEx0Dfy/WGOe/"
    "OSsGj68jw1yrTxQx6i9aHpofRm7yxc+hc/Qm6xxJ1oGEJsEUjfBmUIx+oY8irkut4leSsn"
    "Q/wyAdu0fOnNsm90DWmrvZCJs+wS0xI9kcHTFaGQaMVup40SoptotkYkqK7UI7tqTYSoqt"
    "pNjSKLbtuisOuRZZlJVOq0XXgZV82kXyaf+srXdeZi892uCp7RzN5uzK583h3P63N2yPaL"
    "RyLWwOx5byRRnSIEa5FsKjsdXrK6NrAf6OrceBony6FtgPPRsNlcdHesp+C+DK77Yx0Ucj"
    "8i0tqo2KnYvG7/PolC+jiDOX2Oxw49ANHu5vwurxHRBj6K4ctp6V0WIH0GkJuQKwaJjlw7"
    "c0fyUe4wn8hQv+WqgNfdNo4JyINBiDOaRlNkuzEc7bzLSvhfbY6lwLnaO44Sw2PN2Cx81D"
    "SkJZ+nrIlPyxF1RYiaetmtjC4Yo9lqkHBDBQWJAlLEjv4VqzHkwryXCqs7VmeFITqu/DpQ"
    "mIiC2h9p6xLy0gZORmPppd7nd1+s2ZShLrIrgOn8Q6au+XJXI8AxtLBJgkP6x/yHYeLxlq"
    "R3FJ2Xo5Y8jN2X/ltHH37xvmZvOUyh9lMF6QYJx6Fs4+c53qjzjZTHUR/Gk284kbLekFk1"
    "uel9SSQzJLpd0d9X/1d7mNecrsAnWX2e/Y6j7cfRooI6V3LWwOx1a7077v0ZGGlm4OCxB4"
    "w9QjmlNsV7x/NbDHwY6KvZ6fLXK1uD5hy/GabAU7W83n7yVA9bcZybDIKSQM1vwTPDd4G1"
    "Sl4pwUzBlpTRbZMjBR4iOtX7UmeSLNdiwN8Do4AZEr/ExrfcppeY2tUA3WqLdwi98FmoiY"
    "Mc+aUXeY5S7jlQuKV8pJ94vr2MSk+yaKOHjmPS5ZTr8nI4UyuaFMbih0cgPXFJwAujPlme"
    "L4xW1ckTJEIlvRclir+Fa16aRVYn/cMlXkItkphlEC4owzj4Fs3hOP3dv2YKDc3yjqzw99"
    "xpfES8ZW91bpfuzfq8CiwPXtGVwLa+8SMcnC3ZpD5a5/31OGuxXDsqOmP7OwNFI6TSMleB"
    "rP8MyDsoA2AueSFPEKaUAL4rrcieT0DJMdkXMB8rWzSwxXheDp8DnhUKr8fz1RQB2Y6KPx"
    "9KHDZVTuqHjilGwV0kXRz1YQwm26sNTEwVqSfk94E51Lo+8NFWsT6bDEnVeO80oC7CJ4Eg"
    "4BVgbwZQBfvAD+NWPP7/8H/AQ+Hw=="
)
