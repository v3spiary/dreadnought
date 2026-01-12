<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'

import { FileMinus, MessageSquareText, FileCheck, FileCode } from 'lucide-vue-next';

const router = useRouter()
const input = ref('')
const sending = ref(false)

</script>

<template>
    
    <!-- Модалка -->
    <div id="modal-reader-detail" class="uk-modal-container" uk-modal>
        <div class="uk-modal-dialog uk-modal-body" uk-overflow-auto>
            <div class="uk-container">
                <button class="uk-modal-close-default" type="button" uk-close></button>
                                    
                <article class="uk-article uk-margin-bottom">

                    <h3 class="uk-article-title">Информационный узел</h3>

                    <p class="uk-article-meta">
                        <span class="uk-label uk-margin-xsmall-right uk-margin-xsmall-top">Default</span>
                        <span class="uk-label uk-label-success uk-margin-xsmall-right uk-margin-xsmall-top">Success</span>
                        <span class="uk-label uk-label-warning uk-margin-xsmall-right uk-margin-xsmall-top">Warning</span>
                        <span class="uk-label uk-label-danger uk-margin-xsmall-right uk-margin-xsmall-top">Danger</span>
                    </p>
                    
                    <div>
                        <div uk-grid>
                            <div class="uk-width-auto@m uk-flex-last@m">
                                <ul class="uk-tab-right" uk-tab="connect: #component-tab-right; animation: uk-animation-fade">
                                    <li><a href="#"><FileMinus :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Суммаризация</a></li>
                                    <li><a href="#"><MessageSquareText :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Диаризация</a></li>
                                    <li><a href="#"><FileCheck :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Очищенная расшифровка</a></li>
                                    <li><a href="#"><FileCode :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Исходная расшифровка</a></li>
                                </ul>
                            </div>
                            <div class="uk-width-expand@m">
                                <div id="component-tab-right" class="uk-switcher">
                                    <div>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</div>
                                    <div>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</div>
                                    <div>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur, sed do eiusmod.</div>
                                    <div>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur, sed do eiusmod.</div>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>
            </div>
        </div>
    </div>

    <div uk-filter="target: .js-filter; animation: fade">
        <h3 class="uk-margin-middle-bottom">Audio to Text Transcriptions</h3>

        <div class="uk-grid-small uk-flex-middle" uk-grid>
            <div class="uk-width-expand">

                <div class="uk-grid-small uk-grid-divider uk-child-width-auto" uk-grid>
                    <div>
                        <ul class="uk-subnav uk-subnav-pill" uk-margin>
                            <li class="uk-active" uk-filter-control><a href="#">All</a></li>
                        </ul>
                    </div>
                    <div>
                        <ul class="uk-subnav uk-subnav-pill" uk-margin>
                            <li uk-filter-control="[data-color='white']"><a href="#">White</a></li>
                            <li uk-filter-control="[data-color='blue']"><a href="#">Blue</a></li>
                            <li uk-filter-control="[data-color='black']"><a href="#">Black</a></li>
                        </ul>
                    </div>
                </div>

            </div>
            <div class="uk-width-auto uk-text-nowrap">

                <span class="uk-active" uk-filter-control="sort: data-date"><a class="uk-icon-link" href="#" uk-icon="icon: arrow-down" aria-label="Sort ascending"></a></span>
                <span uk-filter-control="sort: data-date; order: desc"><a class="uk-icon-link" href="#" uk-icon="icon: arrow-up" aria-label="Sort descending"></a></span>

            </div>
        </div>

        <table class="uk-table uk-table-justify uk-table-divider">
            <thead>
                <tr>
                    <th class="uk-width-small">Название</th>
                    <th>Описание</th>
                    <th class="uk-width-small">Статус</th>
                    <th class="uk-width-small">Формат</th>
                    <th>Теги</th>
                    <th class="uk-width-small">Продолжительность</th>
                    <th class="uk-width-small">Дата и время загрузки</th>
                    <th class="uk-width-small">Открыть расшифровку</th>
                </tr>
            </thead>
            <tbody class="js-filter">

                <tr data-color="white" data-date="2016-03-01">
                    <td class="uk-text-bolder">Лекция 2</td>
                    <td>Лекция по теме N, обсуждалось то-то и т.д.</td>
                    <td class="uk-text-muted">
                    <div><span class="uk-label uk-label-warning">В обработке</span></div>
                    </td>
                    <td>MP4 (видео)</td>
                    <td>
                        <div><span class="uk-label">ВШЭ</span></div>
                        <div><span class="uk-label">Лекция</span></div>
                        <div><span class="uk-label">Правовой аудит</span></div>
                    </td>
                    <td>2:31:23</td>
                    <td class="uk-text-muted">09-09-2025 14:30:25</td>
                    <td><a href="#modal-reader-detail" class="uk-button uk-button-default" uk-toggle>Открыть</a></td>
                </tr>

                <tr data-color="blue" data-date="2016-02-01">
                    <td class="uk-text-bolder">Лекция 2</td>
                    <td>Лекция по теме N, обсуждалось то-то и т.д.</td>
                    <td class="uk-text-muted">
                    <div><span class="uk-label uk-label-success">Готово</span></div>
                    </td>
                    <td>MP4 (видео)</td>
                    <td>
                        <div><span class="uk-label">ВШЭ</span></div>
                        <div><span class="uk-label">Лекция</span></div>
                        <div><span class="uk-label">Правовой аудит</span></div>
                    </td>
                    <td>2:31:23</td>
                    <td class="uk-text-muted">09-09-2025 14:30:25</td>
                    <td><a href="#modal-reader-detail" class="uk-button uk-button-default" uk-toggle>Открыть</a></td>
                </tr>

            </tbody>
        </table>
    </div>
</template>
