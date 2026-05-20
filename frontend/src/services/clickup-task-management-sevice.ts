import type { CreateTaskRequest, UpdateTaskRequest } from "@/api/api";
import type { ClickUpTask } from "@/api/api";
import { clickUpTasksApi } from "@/apiClient";

export const clickupTaskManagementService = {
    async createTask(request: CreateTaskRequest): Promise<ClickUpTask | null> {
        if (!request.space_id?.trim()) throw new Error('ClickUp space is required');
        if (!request.list_id?.trim()) throw new Error('ClickUp list is required');
        if (!request.name?.trim()) throw new Error('Task name is required');
        if (!request.description?.trim()) throw new Error('Task description is required');

        const response = await clickUpTasksApi.createTaskClickupTasksManagePost(request);
        return response.data ?? null;
    },

    async updateTask(spaceId: string, request: Omit<UpdateTaskRequest, "space_id">): Promise<ClickUpTask | null> {
        if (!spaceId?.trim()) throw new Error('Click up space code is required');
        
        if (!request.name?.trim()) throw new Error('Task name is required');
        if (!request.description?.trim()) throw new Error('Task description is required');

        const response = await clickUpTasksApi.updateTaskClickupTasksManageSpaceIdPut(spaceId, {
            ...request,
            space_id: spaceId,
        });
        return response.data ?? null;
    },

    async deleteTask(taskId: string): Promise<boolean> {
        if (!taskId?.trim()) throw new Error('Click up task id is required');

        const response = await clickUpTasksApi.deleteTaskClickupTasksManageTaskIdDelete(taskId);
        return response.data ?? false;
    },
};