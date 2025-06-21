RBAC = {
    "BASE": {
        "user:whoami",
        "user:modify_password_own",
        "user:modify_username_own",
    },
    "COLLABORATOR": {
        "collaborator:read",
        "collaborator:update_self",
        "collaborator:delete_self",
        "client:read",
        "contract:read",
        "event:read"
    },
    "MANAGEMENT": {
        "user:read",
        "collaborator:create",
        "collaborator:update_any",
        "collaborator:delete_any",
        "collaborator:modify_role",
        "client:update_unassigned",
        "client:delete_unassigned",
        "contract:create",
        "contract:delete_unassigned",
        "event:modify_support",
        "event:delete"
    },
    "SALES": {
        "client:create",
        "client:update_own",
        "client:delete_own",
        "contract:delete_own",
        "contract:sign_own",
        "contract:modify_total_own",
        "contract:pay_own",
        "event:create",
        "event:update_unassigned",  # can update linked event without support
        "event:delete_unassigned",  # can delete linked event without support
    },
    "SUPPORT": {
        "event:update_own",
    }
}

PERMS = {
    "DEACTIVATED": RBAC["BASE"],
    "ADMIN": RBAC["BASE"],
    "MANAGEMENT": set().union(RBAC["BASE"],
                              RBAC["COLLABORATOR"],
                              RBAC["MANAGEMENT"]),
    "SALES": set().union(RBAC["BASE"],
                         RBAC["COLLABORATOR"],
                         RBAC["SALES"]),
    "SUPPORT": set().union(RBAC["BASE"],
                           RBAC["COLLABORATOR"],
                           RBAC["SUPPORT"]),
}
