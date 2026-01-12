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
    <div id="modal-info-node" class="uk-modal-container" uk-modal>
        <div class="uk-modal-dialog uk-modal-body">
            <div class="uk-container">
                <button class="uk-modal-close-default" type="button" uk-close></button>
                                    
                <article class="uk-article uk-margin-bottom">

                    <h3 class="uk-article-title">Заголовок информационного узла</h3>

                    <p class="uk-article-meta">Written by <a href="#">Super User</a> on 12 April 2012. Posted in <a href="#">Blog</a></p>

                    <p class="uk-text-lead">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip.</p>

                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>

                </article>
            </div>
        </div>
    </div>

    <div uk-filter="target: .js-filter">
        <h3 class="uk-margin-middle-bottom">Information Collector</h3>

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

        <div class="uk-child-width-1-4@s" uk-grid> <!-- Дикий канбан -->
            
            <div>
                <h4>Capture</h4>

                <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">

                    <li data-color="white" data-date="2016-03-01"> <!-- Информационный узел -->
                        <div class="uk-margin">
                            <div class="uk-card uk-card-default uk-card-body uk-card-small">

                                <ul class="uk-iconnav uk-align-right">
                                    <li class="uk-margin-xsmall-top"><a href="#modal-info-node" uk-toggle><span uk-icon="icon: link-external"></span></a></li>
                                </ul>
                            
                                <h6>Длинный или не очень заголовок информационного узла</h6>

                                <span class="uk-label uk-label-danger uk-margin-xsmall-right uk-margin-xsmall-top">Биология</span>
                                <span class="uk-label uk-label-warning uk-margin-xsmall-right uk-margin-xsmall-top">Наблюдение</span>
                                <span class="uk-label uk-label-success uk-margin-xsmall-right uk-margin-xsmall-top">Захвачено</span>
                                <span class="uk-label uk-margin-xsmall-right uk-margin-xsmall-top">A3</span>
                                <span class="uk-label uk-label-danger uk-margin-xsmall-right uk-margin-xsmall-top">C5</span>

                            </div>
                        </div>
                    </li>

                </ul>

            </div>

            <div>
                <h4>Organize</h4>

                <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">

                </ul>

            </div>

            <div>
                <h4>Distill</h4>
                
                <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">


                </ul>

            </div>

            <div>
                <h4>Express</h4>
                
                <ul uk-sortable="group: sortable-group" class="js-filter" style="list-style-type: none; padding-left: 0;">

                </ul>

            </div>

        </div>

    </div>
</template>
