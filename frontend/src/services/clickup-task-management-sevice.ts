import type { CreateTaskRequest, UpdateTaskRequest } from "@/api/api";
import type { ClickUpTask } from "@/api/api";
import { clickUpTasksApi } from "@/apiClient";

export const clickupTaskManagementService = {
    async createTask(request: CreateTaskRequest): Promise<ClickUpTask | null> {
        const response = await clickUpTasksApi.createTaskClickupTasksManagePost(request);
        return response.data ?? null;
    },

    async updateTask(spaceId: string, request: Omit<UpdateTaskRequest, "space_id">): Promise<ClickUpTask | null> {
        const response = await clickUpTasksApi.updateTaskClickupTasksManageSpaceIdPut(spaceId, {
            ...request,
            space_id: spaceId,
        });
        return response.data ?? null;
    },

    async deleteTask(taskId: string): Promise<boolean> {
        const response = await clickUpTasksApi.deleteTaskClickupTasksManageTaskIdDelete(taskId);
        return response.data ?? false;
    },
};