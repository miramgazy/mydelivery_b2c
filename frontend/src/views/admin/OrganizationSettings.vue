<template>
  <div class="max-w-4xl">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
        Настройки организации
      </h2>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <Icon icon="mdi:loading" class="w-8 h-8 animate-spin text-blue-600" />
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
          <Icon icon="mdi:alert-circle" class="w-5 h-5" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- Success -->
      <div
        v-if="successMessage"
        class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
      >
        <div class="flex items-center gap-2 text-green-800 dark:text-green-200">
          <Icon icon="mdi:check-circle" class="w-5 h-5" />
          <span>{{ successMessage }}</span>
        </div>
      </div>

      <!-- Form -->
      <form v-if="!loading" @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Chain ID -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            ID сети (Chain ID) в IIKO
          </label>
          <input
            v-model="form.iiko_chain_id"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите ID чейна (например: c3b91a78-...)"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Идентификатор сети (чейна) в iiko Cloud. Все клиенты остаются в рамках чейна.
          </p>
        </div>

        <!-- Organization ID -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            ID организации в IIKO (Основной / Fallback)
          </label>
          <input
            v-model="form.iiko_organization_id"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите ID организации"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            UUID организации по умолчанию или для одиночной RMS
          </p>
        </div>

        <!-- API Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API ключ от iiko cloud API
          </label>
          <div class="relative">
            <input
              v-model="form.api_key"
              :type="showApiKey ? 'text' : 'password'"
              class="w-full px-4 py-2.5 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Введите API ключ"
              required
            />
            <button
              type="button"
              @click="showApiKey = !showApiKey"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Icon :icon="showApiKey ? 'mdi:eye-off' : 'mdi:eye'" class="w-5 h-5" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            API ключ для доступа к iiko Cloud
          </p>
        </div>

        <!-- RMS Bases List -->
        <div class="p-5 border border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50 dark:bg-gray-800/40 space-y-4">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Icon icon="mdi:store" class="w-5 h-5 text-blue-600" />
                RMS базы филиалов сети (iikoChain)
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Каждая база RMS представляет отдельный ресторан сети для раздельной выгрузки терминалов
              </p>
            </div>
            <button
              type="button"
              @click="openAddRmsModal"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-blue-600 text-white hover:bg-blue-700 rounded-lg font-medium transition-colors"
            >
              <Icon icon="mdi:plus" class="w-4 h-4" />
              Добавить RMS базу
            </button>
          </div>

          <!-- RMS Table -->
          <div v-if="rmsBases.length > 0" class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden bg-white dark:bg-gray-800">
            <table class="w-full text-sm text-left">
              <thead class="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs">
                <tr>
                  <th class="px-4 py-2 font-medium">Филиал</th>
                  <th class="px-4 py-2 font-medium">ID RMS в iiko</th>
                  <th class="px-4 py-2 font-medium">Терминалы</th>
                  <th class="px-4 py-2 font-medium text-right">Действия</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-xs">
                <tr v-for="rms in rmsBases" :key="rms.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td class="px-4 py-2.5 font-medium text-gray-900 dark:text-white">
                    {{ rms.name }}
                  </td>
                  <td class="px-4 py-2.5 font-mono text-gray-500 dark:text-gray-400">
                    {{ rms.iiko_organization_id }}
                  </td>
                  <td class="px-4 py-2.5">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                      {{ rms.terminals_count || 0 }} шт.
                    </span>
                  </td>
                  <td class="px-4 py-2.5 text-right">
                    <div class="inline-flex items-center gap-1">
                      <button
                        type="button"
                        @click="handleSyncSingleRms(rms)"
                        :disabled="syncingRmsId === rms.id"
                        title="Выгрузить терминалы для этой RMS базы"
                        class="px-2 py-1 text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-300 rounded font-medium inline-flex items-center gap-1 disabled:opacity-50"
                      >
                        <Icon :icon="syncingRmsId === rms.id ? 'mdi:loading' : 'mdi:download'" :class="{ 'animate-spin': syncingRmsId === rms.id }" class="w-3.5 h-3.5" />
                        Выгрузить
                      </button>
                      <button
                        type="button"
                        @click="handleDeleteRms(rms)"
                        title="Удалить RMS базу"
                        class="p-1 text-red-500 hover:text-red-700 rounded transition-colors"
                      >
                        <Icon icon="mdi:trash-can-outline" class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-4 text-xs text-gray-500">
            Базы RMS еще не добавлены. Добавьте филиалы сети для раздельной выгрузки терминалов.
          </div>
        </div>

        <!-- Organization Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Название организации
          </label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите название"
          />
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Телефон
          </label>
          <input
            v-model="form.phone"
            type="tel"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="+7 (XXX) XXX-XX-XX"
          />
        </div>

        <!-- Address -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Адрес
          </label>
          <input
            v-model="form.address"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Введите адрес"
          />
        </div>

        <!-- Bot Token -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Токен Telegram бота
          </label>
          <div class="relative">
            <input
              v-model="form.bot_token"
              :type="showBotToken ? 'text' : 'password'"
              autocomplete="off"
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              class="w-full px-4 py-2.5 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Введите токен бота"
            />
            <button
              type="button"
              @click="showBotToken = !showBotToken"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Icon :icon="showBotToken ? 'mdi:eye-off' : 'mdi:eye'" class="w-5 h-5" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Уникальный токен Telegram бота для этой организации
          </p>
        </div>

        <!-- Bot Username -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Юзернейм Telegram бота
          </label>
          <input
            v-model="form.bot_username"
            type="text"
            autocomplete="off"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="username"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Юзернейм бота (без @) для формирования ссылок
          </p>
        </div>

        <!-- TMA Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Shortname Mini App (TMA)
          </label>
          <input
            v-model="form.tma_name"
            type="text"
            autocomplete="off"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="app"
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Например "app", для ссылки возврата в приложение
          </p>
          <div class="mt-4 flex items-center gap-2">
            <button
              type="button"
              @click="handleSetWebhook"
              :disabled="settingWebhook || !form.bot_token"
              class="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <Icon :icon="settingWebhook ? 'mdi:loading' : 'mdi:webhook'" :class="{ 'animate-spin': settingWebhook }" class="w-5 h-5" />
              {{ settingWebhook ? 'Установка...' : 'Установить Webhook' }}
            </button>
            <span v-if="setWebhookResult" class="text-sm" :class="setWebhookSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ setWebhookResult }}
            </span>
          </div>
        </div>

        <!-- Yandex Maps API Key -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            API-ключ Яндекс.Карт (Геокодер)
          </label>
          <div class="relative">
            <input
              v-model="form.yandex_maps_api_key"
              :type="showYandexKey ? 'text' : 'password'"
              autocomplete="off"
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              class="w-full px-4 py-2.5 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                     focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Введите API-ключ Яндекс.Карт"
            />
            <button
              type="button"
              @click="showYandexKey = !showYandexKey"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <Icon :icon="showYandexKey ? 'mdi:eye-off' : 'mdi:eye'" class="w-5 h-5" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Используется для автоматического определения координат по введенному адресу
          </p>
        </div>

        <!-- Webhook для резервной отправки заказов -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ссылка для резервной отправки заказов (вебхук)
          </label>
          <input
            v-model="form.webhook_link"
            type="url"
            autocomplete="off"
            class="w-full px-4 py-2.5 border rounded-lg
                   bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                   focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :class="webhookLinkError ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'"
            placeholder="https://example.com/webhook"
          />
          <p v-if="webhookLinkError" class="mt-1 text-sm text-red-600 dark:text-red-400">
            {{ webhookLinkError }}
          </p>
          <p v-else class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            URL для отправки заказа при сбое доставки в iiko (умный повтор). Оставьте пустым, если не используете.
          </p>
          <div v-if="form.webhook_link" class="mt-2 flex items-center gap-2">
            <button
              type="button"
              @click="handleTestWebhook"
              :disabled="testingWebhook || !!webhookLinkError"
              class="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 dark:bg-amber-900/30 hover:bg-amber-200 dark:hover:bg-amber-900/50 text-amber-800 dark:text-amber-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <Icon :icon="testingWebhook ? 'mdi:loading' : 'mdi:send'" :class="{ 'animate-spin': testingWebhook }" class="w-5 h-5" />
              {{ testingWebhook ? 'Отправка...' : 'Тестировать вебхук' }}
            </button>
            <span v-if="testWebhookResult" class="text-sm" :class="testWebhookSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ testWebhookResult }}
            </span>
          </div>
        </div>

        <!-- Цвет оформления (шапка TMA) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Цвет оформления (шапка TMA)
          </label>
          <div v-if="!showColorPicker" class="flex items-center gap-3 flex-wrap">
            <div
              class="w-12 h-12 rounded-lg border-2 border-gray-300 dark:border-gray-600 flex-shrink-0"
              :style="{ backgroundColor: displayPrimaryColor }"
            />
            <span class="font-mono text-sm text-gray-700 dark:text-gray-300">{{ displayPrimaryColor }}</span>
            <button
              type="button"
              @click="openColorPicker"
              class="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors"
            >
              <Icon icon="mdi:pencil" class="w-5 h-5" />
              Редактировать
            </button>
          </div>
          <div v-else class="p-4 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 space-y-4">
            <div class="flex flex-wrap items-end gap-4">
              <div class="flex flex-col gap-1">
                <span class="text-xs text-gray-500 dark:text-gray-400">Палитра</span>
                <input
                  v-model="colorPickerValue"
                  type="color"
                  class="w-14 h-14 rounded-lg border-2 border-gray-300 dark:border-gray-600 cursor-pointer bg-transparent"
                />
              </div>
              <div class="flex flex-col gap-1 flex-1 min-w-[120px]">
                <span class="text-xs text-gray-500 dark:text-gray-400">Код цвета (например #0284c7)</span>
                <input
                  v-model="colorPickerValue"
                  type="text"
                  maxlength="7"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                  placeholder="#0284c7"
                />
              </div>
            </div>
            <div class="flex gap-2">
              <button
                type="button"
                @click="savePrimaryColor"
                :disabled="savingColor || !isValidHex(colorPickerValue)"
                class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                <Icon :icon="savingColor ? 'mdi:loading' : 'mdi:content-save'" :class="{ 'animate-spin': savingColor }" class="w-5 h-5" />
                {{ savingColor ? 'Сохранение...' : 'Сохранить' }}
              </button>
              <button
                type="button"
                @click="showColorPicker = false"
                class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                Отмена
              </button>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-4 pt-4">
          <button
            type="submit"
            :disabled="saving"
            class="flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700
                   text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon
              :icon="saving ? 'mdi:loading' : 'mdi:content-save'"
              :class="{ 'animate-spin': saving }"
              class="w-5 h-5"
            />
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Modal: Add RMS Base -->
    <div
      v-if="showAddRmsModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
        <div class="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-3">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            Добавить RMS базу филиала
          </h3>
          <button
            type="button"
            @click="closeAddRmsModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <Icon icon="mdi:close" class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleCreateRms" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Название филиала / ресторана
            </label>
            <input
              v-model="rmsForm.name"
              type="text"
              required
              placeholder="Например: Достык, Мега, Доставка Центр"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              ID RMS базы в iiko (UUID)
            </label>
            <input
              v-model="rmsForm.iiko_organization_id"
              type="text"
              required
              placeholder="UUID организации в iiko Cloud"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-xs"
            />
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              @click="closeAddRmsModal"
              class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="addingRms"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {{ addingRms ? 'Сохранение...' : 'Добавить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { useOrganizationStore } from '@/stores/organization'
import organizationService from '@/services/organization.service'

const organizationStore = useOrganizationStore()

const testingWebhook = ref(false)
const testWebhookResult = ref('')
const testWebhookSuccess = ref(false)

const settingWebhook = ref(false)
const setWebhookResult = ref('')
const setWebhookSuccess = ref(false)

async function handleSetWebhook() {
  if (!form.value.bot_token) {
    setWebhookSuccess.value = false
    setWebhookResult.value = 'Сначала введите токен бота'
    return
  }
  
  const orgId = form.value.id || (organizationStore.organization && organizationStore.organization.id)
  if (!orgId) {
    setWebhookSuccess.value = false
    setWebhookResult.value = 'ID организации не найден. Сохраните настройки.'
    return
  }

  settingWebhook.value = true
  setWebhookResult.value = ''
  try {
    await organizationService.setWebhook(orgId)
    setWebhookSuccess.value = true
    setWebhookResult.value = 'Вебхук успешно установлен'
  } catch (err) {
    setWebhookSuccess.value = false
    setWebhookResult.value = err.response?.data?.error || 'Ошибка установки вебхука'
  } finally {
    settingWebhook.value = false
  }
}

function isValidUrl(s) {
  if (!s || typeof s !== 'string') return true
  const t = s.trim()
  if (!t) return true
  try {
    const u = new URL(t)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

const webhookLinkError = computed(() => {
  const v = form.value.webhook_link
  if (!v || !v.trim()) return ''
  if (!isValidUrl(v)) return 'Введите корректную ссылку (http или https)'
  return ''
})

async function handleTestWebhook() {
  if (webhookLinkError.value) return
  testingWebhook.value = true
  testWebhookResult.value = ''
  try {
    await organizationService.testWebhook()
    testWebhookSuccess.value = true
    testWebhookResult.value = 'Тестовый запрос успешно отправлен'
  } catch (err) {
    testWebhookSuccess.value = false
    testWebhookResult.value = err.response?.data?.error || 'Ошибка отправки'
  } finally {
    testingWebhook.value = false
  }
}

watch(() => form.value.webhook_link, () => {
  testWebhookResult.value = ''
})

const displayPrimaryColor = computed(() => {
  const c = form.value.primary_color || ''
  return (c.startsWith('#') ? c : c ? '#' + c : '#0284c7').slice(0, 7)
})

function isValidHex(s) {
  if (!s || typeof s !== 'string') return false
  const t = s.startsWith('#') ? s.slice(1) : s
  return /^[0-9A-Fa-f]{6}$/.test(t)
}

function openColorPicker() {
  colorPickerValue.value = displayPrimaryColor.value
  showColorPicker.value = true
}

async function savePrimaryColor() {
  let hex = colorPickerValue.value.trim()
  if (!hex) return
  const normalized = hex.startsWith('#') ? hex.slice(0, 7) : '#' + hex.slice(0, 6)
  if (!/^#[0-9A-Fa-f]{6}$/.test(normalized)) return
  savingColor.value = true
  try {
    await organizationStore.updateOrganization({ primary_color: normalized })
    form.value.primary_color = normalized
    showColorPicker.value = false
    await loadOrganization()
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось сохранить цвет'
  } finally {
    savingColor.value = false
  }
}

const form = ref({
  id: '',
  iiko_chain_id: '',
  iiko_organization_id: '',
  api_key: '',
  name: '',
  phone: '',
  address: '',
  bot_token: '',
  bot_username: '',
  tma_name: '',
  yandex_maps_api_key: '',
  primary_color: '',
  webhook_link: ''
})

const rmsBases = computed(() => organizationStore.rmsBases || [])
const showAddRmsModal = ref(false)
const rmsForm = ref({ name: '', iiko_organization_id: '' })
const addingRms = ref(false)
const syncingRmsId = ref(null)

const openAddRmsModal = () => {
  rmsForm.value = { name: '', iiko_organization_id: '' }
  showAddRmsModal.value = true
}

const closeAddRmsModal = () => {
  showAddRmsModal.value = false
}

const handleCreateRms = async () => {
  if (!rmsForm.value.name || !rmsForm.value.iiko_organization_id) return
  addingRms.value = true
  try {
    await organizationService.createRmsBase({
      organization: form.value.id,
      name: rmsForm.value.name.trim(),
      iiko_organization_id: rmsForm.value.iiko_organization_id.trim()
    })
    await organizationStore.fetchRmsBases()
    closeAddRmsModal()
    successMessage.value = 'RMS база успешно добавлена'
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка при создании RMS базы'
  } finally {
    addingRms.value = false
  }
}

const handleDeleteRms = async (rms) => {
  if (!confirm(`Удалить RMS базу "${rms.name}"?`)) return
  try {
    await organizationService.deleteRmsBase(rms.id)
    await organizationStore.fetchRmsBases()
    successMessage.value = 'RMS база удалена'
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка при удалении RMS базы'
  }
}

const handleSyncSingleRms = async (rms) => {
  syncingRmsId.value = rms.id
  try {
    const res = await organizationStore.syncRmsTerminals(rms.id)
    successMessage.value = res.message || `Терминалы для ${rms.name} успешно выгружены`
    await organizationStore.fetchRmsBases()
    setTimeout(() => { successMessage.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка синхронизации терминалов'
  } finally {
    syncingRmsId.value = null
  }
}

const showApiKey = ref(false)
const showBotToken = ref(false)
const showYandexKey = ref(false)
const showColorPicker = ref(false)
const colorPickerValue = ref('#0284c7')
const savingColor = ref(false)
const saving = ref(false)
const successMessage = ref('')
const loading = ref(false)
const error = ref(null)

onMounted(async () => {
  await loadOrganization()
})

const loadOrganization = async () => {
  loading.value = true
  error.value = null

  try {
    const org = await organizationStore.fetchOrganization()
    await organizationStore.fetchRmsBases()
    if (org) {
      form.value = {
        id: org.id || '',
        iiko_chain_id: org.iiko_chain_id || '',
        iiko_organization_id: org.iiko_organization_id || '',
        api_key: org.api_key || '',
        name: org.name || '',
        phone: org.phone || '',
        address: org.address || '',
        bot_token: org.bot_token || '',
        bot_username: org.bot_username || '',
        tma_name: org.tma_name || '',
        yandex_maps_api_key: org.yandex_maps_api_key || '',
        primary_color: org.primary_color || '#0284c7',
        webhook_link: org.webhook_link || ''
      }
    }
  } catch (err) {
    error.value = organizationStore.error
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  saving.value = true
  error.value = null
  successMessage.value = ''

  try {
    const payload = {
      ...form.value,
      bot_token: (form.value.bot_token || '').trim(),
      bot_username: (form.value.bot_username || '').trim().replace(/^@+/, ''),
      tma_name: (form.value.tma_name || '').trim()
    }

    await organizationStore.updateOrganization(payload)
    // После сохранения перечитываем данные с сервера (чтобы точно увидеть, что сохранилось)
    await loadOrganization()
    successMessage.value = 'Настройки успешно сохранены'

    // Hide success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    error.value = organizationStore.error || 'Не удалось сохранить настройки'
  } finally {
    saving.value = false
  }
}
</script>
