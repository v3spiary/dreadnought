<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/lib/api'

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
                                    <li><a href="#">14</a></li>
                                    <li><a href="#">25</a></li>
                                    <li><a href="#">36</a></li>
                                </ul>
                            </div>
                            <div class="uk-width-expand@m">
                                <div id="component-tab-right" class="uk-switcher">
                                    <div>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</div>
                                    <div>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</div>
                                    <div>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur, sed do eiusmod.</div>
                                </div>
                            </div>
                        </div>
                    </div>

                </article>

            </div>
        </div>
    </div>

    <div uk-filter="target: .js-filter">

        <h3 class="uk-margin-middle-bottom">Reader Diary</h3>

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

        <div class="uk-child-width-1-4@m uk-grid-small" uk-grid="masonry: pack">

            <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">
                <li data-color="white" data-date="2016-03-01">
                    <div>
                        <div class="uk-card uk-card-default uk-card-hover">
                            <div class="uk-card-media-top">
                                <img src="" width="600px" height="400px" alt="">
                            </div>
                            <div class="uk-card-body">
                                <div class="uk-card-badge uk-label">Брошено</div>
                                <div class="uk-width-expand">
                                    <h3 class="uk-card-title uk-margin-remove-bottom">Мир на Земле</h3>
                                    <p class="uk-text-meta uk-margin-remove-top">Фантастика</p>
                                </div>
                                <p>Автор: С. Лем</p>
                                <a href="#modal-reader-detail" class="uk-button uk-button-text" uk-toggle>Открыть</a>
                            </div>
                        </div>
                    </div>
                </li>
            </ul>

        </div>

    </div>
</template>
