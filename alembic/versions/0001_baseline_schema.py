"""baseline_schema

Revision ID: 0001
Revises:
Create Date: 2026-04-29

PURPOSE
-------
This is the *baseline* migration. It represents the full schema as it exists
in production at the point when Alembic was introduced to the project.

HOW TO HANDLE THIS MIGRATION
-----------------------------

  EXISTING PRODUCTION DB (already has all tables):
      Run this to mark the baseline as applied WITHOUT executing any SQL:

          alembic stamp head

      This tells Alembic "the DB is already at this revision."
      Future `alembic upgrade head` calls will only run revisions AFTER this one.

  FRESH DEVELOPMENT / STAGING ENVIRONMENT (empty DB):
      Run this to create every table from scratch:

          alembic upgrade head

  NEVER run `alembic upgrade head` on a production DB that already has tables —
  use `alembic stamp head` instead.
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None
# ---------------------------------------------------------------------------


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # Tables are created in foreign-key dependency order.
    # The one circular dependency (challenges.previous_winner_id → creations.id
    # AND creations.challenge_id → challenges.id) is handled by:
    #   1. Creating `challenges` WITHOUT the FK to creations
    #   2. Creating `creations` WITH the FK to challenges
    #   3. Adding the deferred FK on `challenges` afterwards
    # This mirrors the SQLAlchemy use_alter=True pattern in the model.
    # -----------------------------------------------------------------------

    # 1. users -----------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("credits", sa.Integer(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("referral_code", sa.String(), nullable=True),
        sa.Column("referred_by_id", sa.Integer(), nullable=True),
        sa.Column("daily_credits", sa.Integer(), nullable=True),
        sa.Column("daily_credits_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["referred_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_referral_code"), "users", ["referral_code"], unique=True)

    # 2. categories -------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("icon", sa.String(length=10), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("preview_url", sa.String(length=500), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=True)

    # 3. styles -----------------------------------------------------------
    op.create_table(
        "styles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("preview_url", sa.String(length=500), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=False),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("credits_required", sa.Integer(), nullable=True),
        sa.Column("uses_count", sa.Integer(), nullable=True),
        sa.Column("is_trending", sa.Boolean(), nullable=True),
        sa.Column("is_new", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_styles_id"), "styles", ["id"], unique=False)
    op.create_index(op.f("ix_styles_category_id"), "styles", ["category_id"], unique=False)
    op.create_index(op.f("ix_styles_name"), "styles", ["name"], unique=False)
    op.create_index(op.f("ix_styles_slug"), "styles", ["slug"], unique=True)

    # 4. challenges (without the deferred FK to creations) ----------------
    op.create_table(
        "challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_image_url", sa.String(length=500), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=False),
        sa.Column("challenge_type", sa.String(length=50), nullable=True),
        sa.Column("day_number", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        # FK to creations.id added AFTER creations table is created (see below)
        sa.Column("previous_winner_id", sa.Integer(), nullable=True),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_challenges_id"), "challenges", ["id"], unique=False)

    # 5. creations --------------------------------------------------------
    op.create_table(
        "creations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("style_id", sa.Integer(), nullable=False),
        sa.Column("original_image_url", sa.String(length=500), nullable=False),
        sa.Column("generated_image_url", sa.String(length=500), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("mood", sa.String(length=50), nullable=True),
        sa.Column("weather", sa.String(length=50), nullable=True),
        sa.Column("dress_style", sa.String(length=50), nullable=True),
        sa.Column("custom_prompt", sa.String(length=200), nullable=True),
        sa.Column("prompt_used", sa.Text(), nullable=True),
        sa.Column("credits_used", sa.Integer(), nullable=True),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("similarity_score", sa.Float(), nullable=True),
        sa.Column("processing_time", sa.Float(), nullable=True),
        sa.Column("likes_count", sa.Integer(), nullable=True),
        sa.Column("views_count", sa.Integer(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"]),
        sa.ForeignKeyConstraint(["style_id"], ["styles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_creations_id"), "creations", ["id"], unique=False)
    op.create_index(op.f("ix_creations_user_id"), "creations", ["user_id"], unique=False)
    op.create_index(op.f("ix_creations_style_id"), "creations", ["style_id"], unique=False)

    # 5b. Deferred FK: challenges.previous_winner_id → creations.id ------
    #     This resolves the circular reference between challenges and creations.
    #     Matches the use_alter=True / name="fk_challenge_winner" in the model.
    op.create_foreign_key(
        "fk_challenge_winner",
        "challenges",
        "creations",
        ["previous_winner_id"],
        ["id"],
    )

    # 6. guest_usages -----------------------------------------------------
    op.create_table(
        "guest_usages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column("style_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["style_id"], ["styles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guest_usages_id"), "guest_usages", ["id"], unique=False)
    op.create_index(op.f("ix_guest_usages_device_id"), "guest_usages", ["device_id"], unique=True)

    # 7. creation_likes ---------------------------------------------------
    op.create_table(
        "creation_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("creation_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["creation_id"], ["creations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "creation_id", name="_user_creation_like_uc"),
    )
    op.create_index(op.f("ix_creation_likes_id"), "creation_likes", ["id"], unique=False)
    op.create_index(op.f("ix_creation_likes_user_id"), "creation_likes", ["user_id"], unique=False)
    op.create_index(op.f("ix_creation_likes_creation_id"), "creation_likes", ["creation_id"], unique=False)

    # 8. collections ------------------------------------------------------
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("cover_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_collections_id"), "collections", ["id"], unique=False)
    op.create_index(op.f("ix_collections_user_id"), "collections", ["user_id"], unique=False)

    # 9. collection_creations (junction table) ----------------------------
    op.create_table(
        "collection_creations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("creation_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creation_id"], ["creations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id", "creation_id", name="_col_creation_uc"),
    )
    op.create_index(op.f("ix_collection_creations_id"), "collection_creations", ["id"], unique=False)
    op.create_index(op.f("ix_collection_creations_collection_id"), "collection_creations", ["collection_id"], unique=False)
    op.create_index(op.f("ix_collection_creations_creation_id"), "collection_creations", ["creation_id"], unique=False)

    # 10. transactions ----------------------------------------------------
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.String(), nullable=False),
        sa.Column("payment_id", sa.String(), nullable=True),
        sa.Column("signature", sa.String(), nullable=True),
        sa.Column("amount_inr", sa.Float(), nullable=False),
        sa.Column("credits_purchased", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(op.f("ix_transactions_order_id"), "transactions", ["order_id"], unique=True)
    op.create_index(op.f("ix_transactions_payment_id"), "transactions", ["payment_id"], unique=True)
    op.create_index(op.f("ix_transactions_status"), "transactions", ["status"], unique=False)

    # 11. credit_transactions ---------------------------------------------
    op.create_table(
        "credit_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_credit_transactions_id"), "credit_transactions", ["id"], unique=False)

    # 12. ad_watches ------------------------------------------------------
    op.create_table(
        "ad_watches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ad_provider", sa.String(length=50), nullable=True),
        sa.Column("ad_unit_id", sa.String(length=100), nullable=True),
        sa.Column("credits_earned", sa.Integer(), nullable=True),
        sa.Column(
            "watched_date",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=True,
        ),
        sa.Column(
            "watched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ad_watches_id"), "ad_watches", ["id"], unique=False)


def downgrade() -> None:
    # Drop in reverse dependency order.
    # Drop the deferred FK first before touching challenges/creations.
    op.drop_index(op.f("ix_ad_watches_id"), table_name="ad_watches")
    op.drop_table("ad_watches")

    op.drop_index(op.f("ix_credit_transactions_id"), table_name="credit_transactions")
    op.drop_table("credit_transactions")

    op.drop_index(op.f("ix_transactions_status"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_payment_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_order_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_id"), table_name="transactions")
    op.drop_table("transactions")

    op.drop_index(op.f("ix_collection_creations_creation_id"), table_name="collection_creations")
    op.drop_index(op.f("ix_collection_creations_collection_id"), table_name="collection_creations")
    op.drop_index(op.f("ix_collection_creations_id"), table_name="collection_creations")
    op.drop_table("collection_creations")

    op.drop_index(op.f("ix_collections_user_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_id"), table_name="collections")
    op.drop_table("collections")

    op.drop_index(op.f("ix_creation_likes_creation_id"), table_name="creation_likes")
    op.drop_index(op.f("ix_creation_likes_user_id"), table_name="creation_likes")
    op.drop_index(op.f("ix_creation_likes_id"), table_name="creation_likes")
    op.drop_table("creation_likes")

    op.drop_index(op.f("ix_guest_usages_device_id"), table_name="guest_usages")
    op.drop_index(op.f("ix_guest_usages_id"), table_name="guest_usages")
    op.drop_table("guest_usages")

    # Remove the deferred FK before dropping the tables involved in the cycle
    op.drop_constraint("fk_challenge_winner", "challenges", type_="foreignkey")

    op.drop_index(op.f("ix_creations_style_id"), table_name="creations")
    op.drop_index(op.f("ix_creations_user_id"), table_name="creations")
    op.drop_index(op.f("ix_creations_id"), table_name="creations")
    op.drop_table("creations")

    op.drop_index(op.f("ix_challenges_id"), table_name="challenges")
    op.drop_table("challenges")

    op.drop_index(op.f("ix_styles_slug"), table_name="styles")
    op.drop_index(op.f("ix_styles_name"), table_name="styles")
    op.drop_index(op.f("ix_styles_category_id"), table_name="styles")
    op.drop_index(op.f("ix_styles_id"), table_name="styles")
    op.drop_table("styles")

    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")

    op.drop_index(op.f("ix_users_referral_code"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
