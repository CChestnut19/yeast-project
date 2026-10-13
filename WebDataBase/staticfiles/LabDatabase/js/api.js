(function (global) {
    'use strict';

    class ApiError extends Error {
        constructor(message, options = {}) {
            super(message);
            this.name = 'ApiError';
            this.status = options.status || 0;
            this.errorCode = options.errorCode || '';
            this.details = options.details;
            this.data = options.data;
        }
    }

    function getApiErrorMessage(data, fallback = '请求处理失败') {
        if (!data) return fallback;

        const error = data.message ?? data.error ?? data.detail ?? data.details;
        if (Array.isArray(error)) {
            return error.filter(Boolean).join('，') || fallback;
        }
        if (typeof error === 'object' && error !== null) {
            return error.message || JSON.stringify(error);
        }
        return String(error || fallback);
    }

    async function apiFetch(url, options = {}) {
        const { timeout = 30000, ...fetchOptions } = options;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...fetchOptions,
                signal: controller.signal,
            });
            const responseText = await response.text();
            let data = null;

            if (responseText) {
                try {
                    data = JSON.parse(responseText);
                } catch (error) {
                    throw new ApiError(
                        response.ok
                            ? '服务器返回了无法识别的数据'
                            : `服务器请求失败（HTTP ${response.status}）`,
                        { status: response.status, data: responseText }
                    );
                }
            }

            if (!response.ok) {
                const fallback = response.status === 401
                    ? '登录状态已失效，请重新登录'
                    : response.status === 403
                        ? '没有操作权限或 CSRF 验证失败'
                        : `请求失败（HTTP ${response.status}）`;
                throw new ApiError(getApiErrorMessage(data, fallback), {
                    status: response.status,
                    errorCode: data?.error_code,
                    details: data?.details,
                    data,
                });
            }

            // 兼容仍以 HTTP 200 返回业务错误的旧接口。
            if (data?.success === false || data?.status === 'failed') {
                throw new ApiError(getApiErrorMessage(data), {
                    status: response.status,
                    errorCode: data?.error_code,
                    details: data?.details,
                    data,
                });
            }

            return data;
        } catch (error) {
            if (error?.name === 'AbortError') {
                throw new ApiError('请求超时，请稍后重试');
            }
            if (error instanceof ApiError) throw error;
            if (error instanceof TypeError) {
                throw new ApiError('网络连接失败，请检查网络或服务器状态');
            }
            throw new ApiError(error?.message || '请求过程中出现未知错误');
        } finally {
            clearTimeout(timeoutId);
        }
    }

    global.ApiError = ApiError;
    global.getApiErrorMessage = getApiErrorMessage;
    global.apiFetch = apiFetch;
})(window);
