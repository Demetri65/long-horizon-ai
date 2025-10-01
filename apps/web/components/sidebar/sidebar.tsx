"use client"
import * as React from "react"
import { Sidebar, SidebarContent } from "@/components/ui/sidebar"
import { SIDEBAR_ITEMS_DATA } from "./sidebar-items"
import { SidebarHead } from "./sidebar-head/sidebar-head"
import { SidebarFoot } from "./sidebar-foot/sidebar-foot"
import { SidebarSection } from "./sidebar-section/sidebar-section"

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar variant="inset" collapsible="icon" {...props}>
      <SidebarHead />
      <SidebarContent className="text-base">
        <SidebarSection label="Main" items={SIDEBAR_ITEMS_DATA} />
      </SidebarContent>
      <SidebarFoot />
    </Sidebar>
  )
}
