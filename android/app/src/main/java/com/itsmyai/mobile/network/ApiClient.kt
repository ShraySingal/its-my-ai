package com.itsmyai.mobile.network

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

/**
 * IT'S MY AI Mobile — Network API Client
 * Manages WebSocket persistent channel and HTTP heartbeats to laptop command center.
 */
class ApiClient {
    private val client = OkHttpClient()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    fun sendHeartbeat(
        serverUrl: String,
        deviceId: String,
        batteryPercent: Int,
        deviceName: String,
        callback: (Boolean, String?) -> Unit
    ) {
        val payload = JSONObject().apply {
            put("device_id", deviceId)
            put("device_name", deviceName)
            put("device_type", "Mobile")
            put("battery_percent", batteryPercent)
            put("status", "online")
            put("capabilities", org.json.JSONArray(listOf("camera", "notifications", "battery", "media")))
        }

        val cleanUrl = serverUrl.trimEnd('/')
        val request = Request.Builder()
            .url("$cleanUrl/api/devices/heartbeat")
            .post(payload.toString().toRequestBody(jsonMediaType))
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(false, e.message)
            }

            override fun onResponse(call: Call, response: Response) {
                val success = response.isSuccessful
                val body = response.body?.string()
                callback(success, body)
            }
        })
    }
}
