"use client";

import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@radix-ui/react-collapsible";
import { ChevronRight } from "lucide-react";
import { SidebarGroup, SidebarGroupLabel, SidebarMenuAction, SidebarMenuButton, SidebarMenuItem, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem } from "../../ui/sidebar";
import { SideBarItemType } from "../sidebar-items";

export interface SidebarSectionProps {
  label?: string;
  items: SideBarItemType[];
}

export const SidebarSection = ({ label, items }: SidebarSectionProps) => {
  return (
    <SidebarGroup>
      {label && <SidebarGroupLabel>{label}</SidebarGroupLabel>}
      {items.map((item) => (
        <Collapsible key={item.title} asChild defaultOpen={item.isActive}>
          <SidebarMenuItem className="list-none">
            <SidebarMenuButton asChild tooltip={item.title}>
              <a href={item.url}>
                <item.icon />
                <span className="text-base">{item.title}</span>
              </a>
            </SidebarMenuButton>
            {item.items?.length ? (
              <>
                <CollapsibleTrigger asChild>
                  <SidebarMenuAction className="data-[state=open]:rotate-90">
                    <ChevronRight />
                    <span className="sr-only">Toggle</span>
                  </SidebarMenuAction>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    {item.items?.map((subItem) => (
                      <SidebarMenuSubItem key={subItem.title}>
                        <SidebarMenuSubButton asChild>
                          <a href={subItem.url}>
                            <span>{subItem.title}</span>
                          </a>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    ))}
                  </SidebarMenuSub>
                </CollapsibleContent>
              </>
            ) : null}
          </SidebarMenuItem>
        </Collapsible>
      ))}
    </SidebarGroup>
  )
}