package com.kiosk.network.model

import com.google.gson.annotations.SerializedName

// Device models
data class DeviceRegisterRequest(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("location_name") val locationName: String,
    val name: String? = null
)

data class DeviceRegisterResponse(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("api_key") val apiKey: String,
    @SerializedName("location_id") val locationId: String,
    @SerializedName("location_name") val locationName: String
)

data class DeviceResponse(
    val id: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("location_id") val locationId: String,
    val name: String? = null,
    @SerializedName("registered_at") val registeredAt: String,
    @SerializedName("last_seen_at") val lastSeenAt: String
)

// Employee models
data class EmployeeCreateRequest(
    @SerializedName("location_id") val locationId: String,
    @SerializedName("employee_id") val employeeId: String,
    val name: String,
    val pin: String
)

data class EmployeeUpdateRequest(
    val name: String? = null,
    val pin: String? = null,
    @SerializedName("is_active") val isActive: Boolean? = null
)

data class EmployeeResponse(
    val id: String,
    @SerializedName("location_id") val locationId: String,
    @SerializedName("employee_id") val employeeId: String,
    val name: String,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

data class EmployeeStateResponse(
    @SerializedName("employee_id") val employeeId: String,
    val name: String,
    val state: String,
    @SerializedName("last_event_time") val lastEventTime: String? = null,
    @SerializedName("last_event_type") val lastEventType: String? = null
)

// Embedding models
data class EmbeddingResponse(
    @SerializedName("employee_id") val employeeId: String,
    val name: String,
    val embedding: List<Float>
)

data class EmbeddingStoreRequest(
    @SerializedName("employee_id") val employeeId: String,
    val embedding: List<Float>
)

// Time event models
data class TimeEventCreateRequest(
    @SerializedName("employee_id") val employeeId: String,
    @SerializedName("event_type") val eventType: String,
    val method: String,
    @SerializedName("event_time") val eventTime: String? = null
)

data class TimeEventUpdateRequest(
    @SerializedName("event_type") val eventType: String? = null,
    @SerializedName("event_time") val eventTime: String? = null,
    @SerializedName("is_valid") val isValid: Boolean? = null
)

data class TimeEventResponse(
    val id: String,
    @SerializedName("employee_id") val employeeId: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("location_id") val locationId: String,
    @SerializedName("event_type") val eventType: String,
    @SerializedName("event_time") val eventTime: String,
    val method: String,
    @SerializedName("is_valid") val isValid: Boolean,
    @SerializedName("created_at") val createdAt: String
)

data class ClockedInEmployeeResponse(
    @SerializedName("employee_id") val employeeId: String,
    val name: String,
    @SerializedName("clock_in_time") val clockInTime: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("device_name") val deviceName: String? = null
)

// Admin models
data class ExportResponse(
    val status: String,
    val message: String,
    val date: String
)

data class StatsResponse(
    @SerializedName("total_employees") val totalEmployees: Int,
    @SerializedName("clocked_in_count") val clockedInCount: Int,
    @SerializedName("clocked_out_count") val clockedOutCount: Int,
    @SerializedName("today_events") val todayEvents: Int
)

// Generic response
data class ApiResponse(
    val status: String,
    val message: String? = null
)

