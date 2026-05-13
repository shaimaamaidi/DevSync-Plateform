import type { CreateTaskRequest, UpdateTaskRequest } from "@/api/api";
import { clickUpTasksApi } from "@/apiClient";

export const clickupTaskManagementService = {
    async createTask(request: CreateTaskRequest): Promise<boolean> {
        await clickUpTasksApi.createTaskClickupTasksManagePost(request);
        return true;
    },

    async updateTask(taskId: string, request: Omit<UpdateTaskRequest, "task_id">): Promise<boolean> {
        await clickUpTasksApi.updateTaskClickupTasksManageTaskIdPut(taskId, {
            ...request,
            task_id: taskId,
        });
        return true;
    },

    async deleteTask(taskId: string): Promise<boolean> {
        await clickUpTasksApi.deleteTaskClickupTasksManageTaskIdDelete(taskId);
        return true;
    },
};