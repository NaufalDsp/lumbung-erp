from enum import Enum
from app.domain.enums import UserRole


class Permission(str, Enum):
    # Admin / System
    MANAGE_USERS_SETTINGS = "manage_users_settings"
    VIEW_AUDIT_LOG = "view_audit_log"

    # Master Data
    MANAGE_PRODUCTS = "manage_products"
    MANAGE_CUSTOMERS = "manage_customers"
    MANAGE_SUPPLIERS = "manage_suppliers"

    # Transactions
    SALES_CREATE_CONFIRM = "sales_create_confirm"
    PURCHASE_CREATE_CONFIRM = "purchase_create_confirm"
    STOCK_RECEIVE_GOODS = "stock_receive_goods"
    STOCK_DELIVER_GOODS = "stock_deliver_goods"
    STOCK_ADJUST = "stock_adjust"
    INVOICE_ISSUE = "invoice_issue"
    PAYMENT_RECORD = "payment_record"

    # Reporting
    VIEW_INVENTORY_VALUATION_COGS = "view_inventory_valuation_cogs"


# Canonical permission matrix adhering strictly to PRD Section 8.3
ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: {
        Permission.MANAGE_USERS_SETTINGS,
        Permission.VIEW_AUDIT_LOG,
        Permission.MANAGE_PRODUCTS,
        Permission.MANAGE_CUSTOMERS,
        Permission.MANAGE_SUPPLIERS,
        Permission.SALES_CREATE_CONFIRM,
        Permission.PURCHASE_CREATE_CONFIRM,
        Permission.STOCK_RECEIVE_GOODS,
        Permission.STOCK_DELIVER_GOODS,
        Permission.STOCK_ADJUST,
        Permission.INVOICE_ISSUE,
        Permission.PAYMENT_RECORD,
        Permission.VIEW_INVENTORY_VALUATION_COGS,
    },
    UserRole.SALES: {
        Permission.MANAGE_CUSTOMERS,
        Permission.SALES_CREATE_CONFIRM,
    },
    UserRole.WAREHOUSE: {
        Permission.MANAGE_PRODUCTS,
        Permission.MANAGE_SUPPLIERS,
        Permission.PURCHASE_CREATE_CONFIRM,
        Permission.STOCK_RECEIVE_GOODS,
        Permission.STOCK_DELIVER_GOODS,
        Permission.STOCK_ADJUST,
    },
    UserRole.FINANCE: {
        Permission.MANAGE_CUSTOMERS,
        Permission.INVOICE_ISSUE,
        Permission.PAYMENT_RECORD,
        Permission.VIEW_INVENTORY_VALUATION_COGS,
    },
}


def has_permission(role: str | UserRole, permission: Permission) -> bool:
    """Verifies whether a given role holds the requested permission."""
    try:
        user_role = UserRole(role) if isinstance(role, str) else role
    except ValueError:
        return False

    return permission in ROLE_PERMISSIONS.get(user_role, set())


def get_permissions_for_role(role: str | UserRole) -> list[str]:
    """Retrieves all string permission keys associated with a role."""
    try:
        user_role = UserRole(role) if isinstance(role, str) else role
        return [p.value for p in ROLE_PERMISSIONS.get(user_role, set())]
    except ValueError:
        return []
