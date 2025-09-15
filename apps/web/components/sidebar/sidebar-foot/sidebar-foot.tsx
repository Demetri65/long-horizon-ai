"use client";

import { SidebarFooter } from "../../ui/sidebar";
import { NavUser } from "./nav-user";
import { SIDEBAR_ITEMS_DATA } from "../sidebar-items";

const user = {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
}

export const SidebarFoot = () => {
    return (
        <SidebarFooter>
            <NavUser user={user} />
        </SidebarFooter>
    )
}