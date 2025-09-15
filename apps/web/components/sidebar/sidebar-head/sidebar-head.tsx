"use client";

import { 
    SidebarHeader, 
    SidebarMenu, 
    SidebarMenuButton, 
    SidebarMenuItem, 
    SidebarTrigger 
} from "../../ui/sidebar";

export const SidebarHead = () => {
    return (
        <SidebarHeader>
            <SidebarMenu>
            <SidebarMenuItem className="flex items-center justify-between">
                <SidebarMenuButton size="lg" asChild>
                <SidebarTrigger size="lg" className="h-8 w-8"/>
                </SidebarMenuButton>
            </SidebarMenuItem>
            </SidebarMenu>
        </SidebarHeader>
    )
};